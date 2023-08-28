import asyncio
import os
import sys
import discord
import json
import os
import random
import string
from discord import Intents, Client, Interaction
from discord.app_commands import CommandTree

#region 初期設定

# 現在のスクリプトの絶対パスを取得
exe_path = os.path.abspath(sys.argv[0])

current_path = os.path.dirname(exe_path)

#current_path = os.path.dirname(os.path.abspath(__file__))

# 基本の設定ファイル
# discordbot_config.jsonへの相対パスを作成
config_path = os.path.join(current_path, "discordbot_config.json")
# 規約同意からロール付与用の設定ファイル
agree_path = os.path.join(current_path, 'discordbot_agree.json')
# 招待コード用とロール付与用のファイル
invite_path = os.path.join(current_path, "discordbot_invite.json")
# NGワード用のファイル
# ng_path = os.path.join(current_path, "discordbot_ng.json")

# discordbot_configを読み込む
with open(config_path, encoding="utf-8") as f:
    config_data = json.load(f)
# # discordbot_agreeを読み込む
with open(agree_path, encoding='utf-8') as f:
    agree_data = json.load(f)
# # discordbot_inviteを読み込む
# with open(invite_path, encoding="utf-8") as f:
#     invite_data = json.load(f)

# 設定ファイルから取得
TOKEN = config_data["DISCORD_BOT_TOKEN"]

# コマンドを同期する
class MyClient(Client):
    def __init__(self, intents: Intents) -> None:
        super().__init__(intents=intents)
        self.tree = CommandTree(self)

    async def setup_hook(self) -> None:
        await self.tree.sync()

# 接続に必要なオブジェクトを生成
# intents = Intents.all()

intents = Intents.default()
intents.members = True
intents.message_content = True

client = MyClient(intents=intents)
invite_uses = {}
# endregion

#region 招待コードにロール紐づけ関連

@client.tree.command(name='invite_connect', description="招待コードにロールを紐づけます。既に付いている場合は上書きします。")
async def invite_connect(interaction: Interaction, invite_code: str, role: discord.Role):
    print(f"{invite_code}  {role}")
    
    # URLになっている場合コードのみにトリミングする
    if invite_code.startswith("https://discord.gg/"):
        invite_code = invite_code[len("https://discord.gg/"):]
    
    invite_data = await get_invite_data()
    await update_invite_data(interaction, invite_code, role, invite_data)
    await save_invite_data(invite_data)
    await get_invite_uses(client)

@client.tree.command(name='invite_list', description="現在サーバー上に作成されている招待リンクを全て表示します。")
async def invite_list(interaction: Interaction):

    await interaction.response.defer(ephemeral=True)

    # サーバー上に存在しない招待コードを削除する。
    await remove_missing_invites(interaction.guild)
    
    # JSONファイルを読み込む
    invite_data = await get_invite_data()

    # interaction.guild.idに一致するデータを取得
    guild_id = str(interaction.guild.id)
    guild_data = None
    for item in invite_data:
        # "GUILD_ID_" をトリミング
        item_id = next(iter(item)).replace("GUILD_ID_", "")
        if item_id == guild_id:
            guild_data = item
            break

    # サーバー情報がない場合、JSONに"GUILD_ID"を書き込んで再度取得する
    if not guild_data:
        guild_data = {f"GUILD_ID_{interaction.guild.id}": []}
        invite_data.append(guild_data)

        # JSONファイルに書き込む
        with open(invite_path, 'w', encoding='utf-8') as f:
            json.dump(invite_data, f, indent=4)

    # レスポンスとして加工した情報を取得
    formatted_data = await format_guild_data(guild_data, interaction.guild)

    # ギルドデータから招待コードを取得
    invite_codes = []
    for records in guild_data.values():
        for record in records:
            invite_codes.append(record["INVITE_CODE"])

    # 未使用の招待コードを取得
    unused_codes = []
    invites = await interaction.guild.invites()
    for invite in invites:
        # 既存の招待コードに含まれていない場合、未使用の招待コードとして追加
        if invite.code not in invite_codes:
            unused_codes.append(invite.code)

    # 未使用の招待コードが存在する場合、文言を作成
    if unused_codes:
        formatted_data += "\nロールが付与されていない招待コード:\n"

        # チャンネル情報の追加
        for unused_code in unused_codes:
            try:
                invite = await client.fetch_invite(unused_code)
                if invite.guild is not None:
                    guild = invite.guild
                    channel = invite.channel
                    channel_name = channel.name if channel else "チャンネルが見つかりません"
                    formatted_data += f"招待コード: https://discord.gg/{unused_code}\nチャンネル: {channel_name}\n\n"
            except discord.NotFound:
                continue

    # 文字列を行ごとに分割し、それぞれの行を分割して処理する
    formatted_data_parts = []
    current_part = ""
    for line in formatted_data.split("\n"):
        # 現在の部分と次の行を追加したときに2000文字を超える場合は、新しい部分を開始する
        if len(current_part + line) > 2000:
            formatted_data_parts.append(current_part)
            current_part = line
        else:
            current_part += line + "\n"

    # 最後の部分を追加する
    formatted_data_parts.append(current_part)

    # 分割した各部分をそれぞれ別のメッセージとして送信
    for i, data_part in enumerate(formatted_data_parts):
        embed = discord.Embed(title=f"招待コードリスト ({i+1}/{len(formatted_data_parts)})", description=data_part, color=discord.Colour.red())
        await interaction.followup.send(embed=embed, ephemeral=True)
        await asyncio.sleep(1)


@client.tree.command(name='invite_delete', description="招待コードの紐づけを削除します。")
async def invite_delete(interaction: Interaction, invite_code: str):
    if invite_code.startswith("https://discord.gg/"):
        invite_code = invite_code[len("https://discord.gg/"):]

    invite_data = await get_invite_data()

    deleted = False
    deleted_entries = []
    for item in invite_data:
        guild_id = list(item.keys())[0]
        if guild_id == f"GUILD_ID_{interaction.guild.id}":
            content = item[guild_id]
            for code_item in content:
                if code_item["INVITE_CODE"] == invite_code:
                    role_id = code_item["ROLE_ID"]
                    role = interaction.guild.get_role(role_id)
                    content.remove(code_item)
                    deleted = True
                    deleted_entries.append({"ROLE_ID": role_id, "INVITE_CODE": invite_code, "ROLE_NAME": role.name if role else "Unknown Role"})
                    break

    if not deleted:
        await interaction.response.send_message("該当する招待コードが見つかりませんでした", ephemeral=True)
        return

    await save_invite_data(invite_data)

    deleted_message = "\n".join([f"\n招待コード: {entry['INVITE_CODE']}\nロール: {entry['ROLE_NAME']}" for entry in deleted_entries])
    await interaction.response.send_message(f"削除しました\n{deleted_message}", ephemeral=True)

@client.tree.command(name='invite_alldelete', description="全ての招待コードの紐づけを削除します。実行する場合はconfirmationにOKと入力してください。")
async def invite_alldelete(interaction: Interaction, confirmation: str):
    # 引数がOKでなければリターンする
    if confirmation != "OK":
        await interaction.response.send_message("実行されませんでした。\n`confirmation` に `OK` と入力してください。", ephemeral=True)
        return  
    
    invite_data = await get_invite_data()

    deleted = False
    for item in invite_data:
        guild_id = list(item.keys())[0]
        if guild_id == f"GUILD_ID_{interaction.guild.id}":
            invite_data.remove(item)
            deleted = True
            break

    if not deleted:
        await interaction.response.send_message("該当する招待コードが見つかりませんでした", ephemeral=True)
        return

    await save_invite_data(invite_data)

    await interaction.response.send_message("全ての招待コードの紐づけを削除しました", ephemeral=True)

#ギルドデータを整える
async def format_guild_data(guild_data, guild):
    formatted_data = ""
    for record in next(iter(guild_data.values())):
        invite_code = record["INVITE_CODE"]
        role_id = record["ROLE_ID"]

        # 招待コードをフェッチし、エラーが発生したら次のレコードへ
        try:
            invite = await client.fetch_invite(invite_code)
        except discord.NotFound:
            continue

        channel_name = invite.channel.name if invite.channel else "チャンネルが見つかりません"
        role_name = guild.get_role(role_id).name if guild.get_role(role_id) else "ロールが見つかりません"

        formatted_data += f"招待コード: https://discord.gg/{invite_code}\nチャンネル: {channel_name}\nロール: {role_name}\n\n"
    return formatted_data



#サーバー上に存在しない招待コードを削除する。
async def remove_missing_invites(guild):
    guild_id = f"GUILD_ID_{guild.id}"
    
    # JSONファイルを読み込む
    with open(invite_path, encoding='utf-8') as f:
        json_data = json.load(f)
    
    deleted = False

    for item in json_data:
        if guild_id in item:
            content = item[guild_id]

            # サーバーから取得した招待コードとJSONから取得した招待コードを比較して、存在しないものを削除する
            existing_invite_codes = []
            invites = await guild.invites()
            for invite in invites:
                existing_invite_codes.append(invite.code)
            
            updated_content = [record for record in content if record["INVITE_CODE"] in existing_invite_codes]
            item[guild_id] = updated_content  # JSONデータの更新
            deleted = True

    # 更新されたJSONデータをファイルに書き込む
    with open(invite_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=4)

# 招待コードの使用人数を取得する
async def get_invite_uses(client):
    invite_uses = {}
    for guild in client.guilds:
        invite_uses[guild.id] = {}
        invites = await guild.invites()
        for invite in invites:
            invite_uses[guild.id][invite.code] = invite.uses
    return invite_uses

# JSONデータを更新する
async def update_invite_data(interaction, invite_code, role, invite_data):
    guild_id = f"GUILD_ID_{interaction.guild.id}"
    overwrite_message = "上書きしました！\n\n招待コード: https://discord.gg/{invite_code}\nロール: {role.name}"
    register_message = "登録しました！\n\n招待コード: https://discord.gg/{invite_code}\nロール: {role.name}"

    # サーバーの招待コードを全て取得
    invites = await interaction.guild.invites()
    # invite_codeがサーバーに存在するか確認
    if not any(invite.code == invite_code for invite in invites):
        # invite_codeが存在しない場合はメッセージを送り処理を終了
        await interaction.response.send_message("存在しない招待コードです。", ephemeral=True)
        return

    # ギルドごとのデータを探索
    for item in invite_data:
        if guild_id in item:
            # ギルドのデータが存在する場合
            content = item[guild_id]

            # 既存の招待コードと一致するか確認
            for index, code_item in enumerate(content):
                if code_item["INVITE_CODE"] == invite_code:
                    # 既存の招待コードと一致する場合は上書き
                    content[index] = {
                        "INVITE_CODE": invite_code,
                        "ROLE_ID": role.id
                    }
                    await interaction.response.send_message(overwrite_message.format(invite_code=invite_code, role=role), ephemeral=True)
                    return

            # 既存の招待コードと一致しない場合は追加
            content.append({
                "INVITE_CODE": invite_code,
                "ROLE_ID": role.id
            })
            await interaction.response.send_message(register_message.format(invite_code=invite_code, role=role), ephemeral=True)
            return

    # ギルドに関するデータが存在しない場合は新しいデータを作成
    new_item = {
        guild_id: [
            {
                "INVITE_CODE": invite_code,
                "ROLE_ID": role.id
            }
        ]
    }
    invite_data.append(new_item)
    await interaction.response.send_message(register_message.format(invite_code=invite_code, role=role), ephemeral=True)

# JSONを読み込む
async def get_invite_data():
    with open(invite_path, encoding='utf-8') as f:
        invite_data = json.load(f)
    return invite_data

# JSONを保存
async def save_invite_data(invite_data):
    with open(invite_path, 'w', encoding='utf-8') as f:
        json.dump(invite_data, f, indent=4)

#endregion

#region 投票関連

# 投票情報を格納する辞書
votes = {}
# 投票に使用する絵文字の設定
YES_NO_EMOJIS = ["⭕", "❌"]
VOTE_EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

@client.tree.command(name="vote_yesno", description="YES or Noの投票を行います。")
async def vote_yesno(interaction: Interaction, votetext: str):
    # 投票を開始する一時的なメッセージを送信します
    await interaction.response.send_message("投票を開始します...", ephemeral=True)

    # 質問文の作成
    embed = discord.Embed(title=votetext, description="", color=discord.Colour.red())
    # 投票コードの生成
    vote_code = generate_vote_code("yesno")

    # 投票コードを表示
    embed.set_footer(text=f"投票コード: `{vote_code}`")

    # メッセージを送信
    message = await interaction.followup.send(embed=embed)

    # リアクションによる回答欄を作成
    for emoji in YES_NO_EMOJIS:
        await message.add_reaction(emoji)

    # 投票情報を保存
    votes[vote_code] = {
        "message_id": message.id,
        "votetext": votetext,
        "choices": ["YES", "NO"],
    }

@client.tree.command(name="vote_choice", description="複数択の投票を行います。")
async def vote_choice(
    interaction: Interaction,
    votetext: str,
    choice1: str,
    choice2: str,
    choice3: str = None,
    choice4: str = None,
    choice5: str = None,
    choice6: str = None,
    choice7: str = None,
    choice8: str = None,
    choice9: str = None,
    choice10: str = None,
):
    choices = [
        choice
        for choice in [
            choice1,
            choice2,
            choice3,
            choice4,
            choice5,
            choice6,
            choice7,
            choice8,
            choice9,
            choice10,
        ]
        if choice is not None
    ]

    # 投票を開始する一時的なメッセージを送信します
    await interaction.response.send_message("投票を開始します...", ephemeral=True)

    # 質問文の作成
    embed = discord.Embed(title=votetext, description="", color=discord.Colour.red())

    # 選択肢の作成
    for i, choice in enumerate(choices):
        embed.description = (
            embed.description + VOTE_EMOJIS[i] + "   " + choices[i] + "\n"
        )

    # 投票コードの生成
    vote_code = generate_vote_code("choice")

    # 投票コードを表示
    embed.set_footer(text=f"投票コード: `{vote_code}`")

    # メッセージを送信
    message = await interaction.followup.send(embed=embed)

    # リアクションによる回答欄を作成
    for i in range(len(choices)):
        await message.add_reaction(VOTE_EMOJIS[i])

    # 投票情報を保存
    votes[vote_code] = {
        "message_id": message.id,
        "vote_counts": [0] * len(choices),
        "votetext": votetext,
        "choices": choices,
    }

@client.tree.command(name="vote_end", description="投票を締め切り、集計します。")
async def vote_end(interaction: Interaction, vote_code: str):
    if vote_code in votes:
        # 集計の開始をユーザーに伝える
        await interaction.response.send_message("集計を開始します...", ephemeral=True)

        # 集計処理を非同期に行う
        asyncio.create_task(tally_votes(interaction, vote_code))
    else:
        await interaction.response.send_message("指定された投票コードは見つかりませんでした", ephemeral=True)

# 集計する
async def tally_votes(interaction, vote_code):
    # 投票情報を取得
    vote_info = votes[vote_code]
    message_id = vote_info["message_id"]
    votetext = vote_info["votetext"]
    choices = vote_info["choices"]

    # メッセージを取得
    message = await interaction.channel.fetch_message(message_id)

    # 選択肢毎のカウントを保持する辞書を作成
    counts = {choice: 0 for choice in choices}

    # リアクションから集計を行う
    for reaction in message.reactions:
        # vote_codeの頭文字で分岐する
        if vote_code.startswith("C"):
            emojis = VOTE_EMOJIS
        elif vote_code.startswith("Y"):
            emojis = YES_NO_EMOJIS

        # 対応するリアクションの場合、カウントを更新
        if str(reaction.emoji) in emojis:
            choice_index = emojis.index(str(reaction.emoji))
            choice = choices[choice_index]
            counts[choice] = reaction.count - 1

    # 最も票が多かった選択肢を見つける
    max_votes = max(counts.values())
    winners = [choice for choice, count in counts.items() if count == max_votes]

    # 集計結果を表示
    result_embed = discord.Embed(
        title=f"投票結果: {votetext}", color=discord.Colour.green()
    )
    for choice, count in counts.items():
        # 勝者には王冠の絵文字を追加
        if choice in winners:
            result_embed.add_field(name=f"👑 {choice}", value=f"票数: {count}")
        else:
            result_embed.add_field(name=choice, value=f"票数: {count}")

    # 集計結果を送信し、メッセージを削除
    await interaction.channel.send(embed=result_embed)
    await message.delete()

    # 投票情報を削除
    del votes[vote_code]

# ランダムな投票コードを生成する
def generate_vote_code(style: str):
    while True:
        # voteの種類によって頭に固定文字を付ける
        if style == "yesno":
            fixed_string = "Y"
        elif style == "choice":
            fixed_string = "C"
        # ランダム文字列を作る
        random_string = "".join(
            random.choice(
                string.ascii_uppercase + string.ascii_lowercase + string.digits
            )
            for _ in range(6)
        )
        vote_code = fixed_string + random_string
        # 既に存在する投票コードと重複する場合はやり直す
        if vote_code not in votes:
            break
    # 作られたコードを返す
    return vote_code

# endregion

#region 規約同意関連

@client.tree.command(name="link_agree_message", description="規約メッセージへの紐づけをします")
async def link_agree_message(interaction: Interaction, message_id: str, role: discord.Role):
     # 無効なメッセージIDの場合はエラーメッセージを送信して終了
    if not message_id.isdigit():
        await interaction.response.send_message("メッセージIDが無効な値です。メッセージIDを確認してください。", ephemeral=True)
        return

    role_id = role.id  # ロールのIDを取得

    new_data = {
        "GUILD_ID": interaction.guild.id,
        "AGREE": {
            "MESSAGE_ID": message_id,
            "ROLE_ID": role_id
        }
    }

    # JSONファイルの読み込み
    with open(agree_path, encoding='utf-8') as f:
        agree_data = json.load(f)
    
    updated = False
    for i, data in enumerate(agree_data):
        if data["GUILD_ID"] == new_data["GUILD_ID"]:
            agree_data[i] = new_data
            updated = True
            break
    
    #文言の変数
    overwrite_message = "規約メッセージ登録を上書きしました。"
    new_register_message = "規約メッセージを新規登録しました。"
    not_found_message = "メッセージは見つかりませんでした。\nメッセージIDを確認してください。"
    
    if updated:
        # 上書きの場合
        message_content = None
        for channel in interaction.guild.text_channels:
            try:
                message = await channel.fetch_message(message_id)
                message_content = message.content
                break
            except discord.NotFound:
                pass
        
        # 上書き完了のメッセージ送信
        if message_content:
            await interaction.response.send_message(
                f"{overwrite_message}\n"
                f"(https://discord.com/channels/{interaction.guild.id}/{channel.id}/{message_id})",
                ephemeral=True
            )
        # エラーメッセージ送信
        else:
            await interaction.response.send_message(f"{not_found_message}",ephemeral=True)
    else:
        # 新規登録の場合
        agree_data.append(new_data)
        message_content = None
        for channel in interaction.guild.text_channels:
            try:
                message = await channel.fetch_message(message_id)
                message_content = message.content
                break
            except discord.NotFound:
                pass
        # 登録完了のメッセージ送信
        if message_content:
            await interaction.response.send_message(
                f"{new_register_message}\n"
                f"(https://discord.com/channels/{interaction.guild.id}/{channel.id}/{message_id})",
                ephemeral=True
            )
        # エラーメッセージ送信
        else:
            await interaction.response.send_message(f"{not_found_message}",ephemeral=True)

    # JSONファイルの書き込み
    with open(agree_path, 'w', encoding='utf-8') as file:
        json.dump(agree_data, file, indent=4)

@client.tree.command(name="link_agree_delete", description="規約メッセージへの紐づけを解除します。実行する場合はconfirmationにOKと入力してください。")
async def link_agree_delete(interaction: Interaction, confirmation: str):
    # 引数がOKでなければリターンする
    if confirmation != "OK":
        await interaction.response.send_message("実行されませんでした。\n`confirmation` に `OK` と入力してください。", ephemeral=True)
        return
    
    guild_id = interaction.guild.id

    # JSONファイルの読み込み
    with open(agree_path, 'r', encoding='utf-8') as file:
        agree_data = json.load(file)

    # ギルドIDに一致するデータを削除
    updated = False
    for i, data in enumerate(agree_data):
        if data["GUILD_ID"] == guild_id:
            del agree_data[i]
            updated = True
            break

    if updated:
        # JSONファイルの書き込み
        with open(agree_path, 'w', encoding='utf-8') as file:
            json.dump(agree_data, file, indent=4)
        await interaction.response.send_message("規約メッセージへの連携を解除しました。", ephemeral=True)
    else:
        await interaction.response.send_message("削除するデータがありませんでした。", ephemeral=True)

#endregion

# 起動時に動作する処理 招待コードの内部処理在中
@client.event
async def on_ready():
    # コマンドの同期
    await client.setup_hook()
    # 起動したらターミナルにログイン通知が表示される
    print("SA-BOTがログインしました")

    # 招待コードの利用人数を取得する
    global invite_uses
    invite_uses = await get_invite_uses(client)

# ユーザーがサーバーに参加した時の処理 招待コードの内部処理在中
@client.event
async def on_member_join(member):
    global invite_uses
    invites = await member.guild.invites()

    # region 招待コードからロール付与の処理

    for invite in invites:
        # get()メソッドを使用して、invite.codeが存在しない場合は0をデフォルト値として使用
        if invite_uses.get(member.guild.id, {}).get(invite.code, 0) < invite.uses:
            print(f"{member.name} joined using {invite.url}")

            # 招待コードの使用人数を修正する。
            if member.guild.id not in invite_uses:
                invite_uses[member.guild.id] = {}
            invite_uses[member.guild.id][invite.code] = invite.uses

            with open(invite_path, encoding="utf-8") as f:
                invite_data = json.load(f)

            guild_id = f"GUILD_ID_{member.guild.id}"
            for data in invite_data:
                if guild_id in data:
                    for item in data[guild_id]:
                        if item["INVITE_CODE"] == invite.code:
                            role = discord.utils.get(
                                member.guild.roles, id=item["ROLE_ID"]
                            )
                            await member.add_roles(role)
                            break
    # endregion

# ユーザーがリアクションした時の処理 規約同意した人にロール付与の処理在中
@client.event
async def on_raw_reaction_add(payload):
    # Botがリアクションした場合は処理を終了
    if payload.user_id == client.user.id:
        return

    # JSONファイルの読み込み
    with open(agree_path, encoding='utf-8') as f:
        agree_data = json.load(f)

    # guild_id から Guild オブジェクトを取得
    guild = client.get_guild(payload.guild_id)

    # user_id から Member オブジェクトを取得
    member = guild.get_member(payload.user_id)

    # region 規約に同意した人にロール付与の処理

    # サーバーIDがJsonと一致するものを探す
    for item in agree_data:
        if item["GUILD_ID"] == guild.id:
            # メッセージIDがJsonと一致しなければリターン
            if str(payload.message_id) != item["AGREE"]["MESSAGE_ID"]:
                return
            # リアクションが✅でなければリターン
            if payload.emoji.name != "✅":
                return
            # ロールを付与する
            role_id = item["AGREE"]["ROLE_ID"]
            role = guild.get_role(role_id)
            await member.add_roles(role)

            # リプライを送りたい場合は以下を使用する。
            # channel = client.get_channel(payload.channel_id)
            # message_sent = await channel.send(f'{member.mention}さんが {role.name}になりました')
            break
    # endregion

# BOTを起動する処理　これより下あるものは実行されないので注意
client.run(TOKEN)