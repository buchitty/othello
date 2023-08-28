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

# 基本の設定ファイル
# discordbot_config.jsonへの相対パスを作成
config_path = os.path.join(current_path, "discordbot_config.json")
# NGワード用のファイル
ng_path = os.path.join(current_path, "discordbot_ng.json")

# discordbot_configを読み込む
with open(config_path, encoding="utf-8") as f:
    config_data = json.load(f)

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

#region NGワード関連

@client.tree.command(name="ng_word_add", description="NGワードを登録します")
async def ng_word_add(interaction: Interaction, ng_word: str):
    json_file = ng_path

    with open(json_file, "r", encoding='utf-8') as file:
        json_data = json.load(file)

    # コマンドを実行したギルドIDを取得
    guild_id = interaction.guild_id  

    # 対象のギルドIDが存在するかチェック
    for item in json_data:
        if item.get("GUILD_ID") == guild_id:
            target_messages = item.get("TARGET_MESSAGE")  

            # 追加するワードがすでに存在するかをチェック
            if any(target_message.get("CONTENT") == ng_word for target_message in target_messages):
                await interaction.response.send_message(f"'{ng_word}' は既にNGリストに存在します。", ephemeral=True)
                return

            target_messages.append({"CONTENT": ng_word})
            break
    else:
        # ギルドIDが存在しない場合は新たにギルドデータを作成
        json_data.append({"GUILD_ID": guild_id, "ROLE_ID": 0, "CHANNEL_ID": 0, "TARGET_MESSAGE": [{"CONTENT": ng_word}]})

    # 更新したJSONデータをファイルに書き込む
    with open(json_file, "w", encoding='utf-8') as file:
        json.dump(json_data, file, ensure_ascii=False, indent=4) 

    await interaction.response.send_message(f"NGリストに '{ng_word}' を追加しました。", ephemeral=True)

@client.tree.command(name="ng_word_delete", description="NGワードの登録を解除します")
async def ng_word_delete(interaction: Interaction, ng_word: str):
    # JSONファイルのパスを指定します
    json_file = ng_path

    # JSONデータを読み込む
    with open(json_file, "r", encoding='utf-8') as file:
        json_data = json.load(file)

    # コマンドを実行したギルドIDを取得
    guild_id = interaction.guild_id  

    # 対象のギルドIDが存在するかチェック
    for item in json_data:
        if item.get("GUILD_ID") == guild_id:
            target_messages = item.get("TARGET_MESSAGE")

            # 削除するワードが存在するかをチェック
            for i, target_message in enumerate(target_messages):
                if target_message.get("CONTENT") == ng_word:
                    # ワードを削除
                    del target_messages[i]  

                    # 更新したJSONデータをファイルに書き込む
                    with open(json_file, "w", encoding='utf-8') as file:
                        json.dump(json_data, file, ensure_ascii=False, indent=4)

                    # ユーザーに削除完了を通知
                    await interaction.response.send_message(f"NGリストから '{ng_word}' を削除しました。", ephemeral=True)
                    return

    # 削除するワードが見つからなかった場合、ユーザーに通知
    await interaction.response.send_message(f"'{ng_word}' はNGリストに存在しません。", ephemeral=True)

@client.tree.command(name="ng_word_list", description="NGワードの一覧と関連情報を表示します")
async def ng_word_list(interaction: Interaction):

    await interaction.response.defer(ephemeral=True)

    # 文言の変数
    not_found_message = "このギルドのNGワードリストは存在しません。"
    no_data_message = "設定されていません。"

    # 所定のJSONファイルのパス
    json_file = ng_path

    # JSONデータを読み込む
    with open(json_file, "r", encoding="utf-8") as file:
        json_data = json.load(file)

    guild = interaction.guild  # コマンドを実行したギルドを取得

    # 対象のギルドIDが存在するかチェック、存在すれば対象メッセージとロールをリストとして表示
    for item in json_data:
        if item.get("GUILD_ID") == guild.id:
            target_messages = item.get("TARGET_MESSAGE")
            role_id = item.get("ROLE_ID")  # ロールIDを取得
            channel_id = item.get("CHANNEL_ID")  # チャンネルIDを取得

            # NGワードリストが存在するかチェック
            if target_messages:
                ng_word_list = "\n".join(target_message.get("CONTENT") for target_message in target_messages)
            else:
                ng_word_list = "NGワードリストがありません。"

            # ロールとチャンネルを取得
            role = discord.utils.get(guild.roles, id=role_id) if role_id else None
            channel = discord.utils.get(guild.channels, id=channel_id) if channel_id else None

            # メッセージを構築
            message = "付与されるロール:\n{}\n\n通知チャンネル:\n{}\n\nNGワードリスト:\n{}".format(
                role.name if role else no_data_message,
                channel.mention if channel else no_data_message,
                ng_word_list
            )

            # 2000文字で分割する
            message_parts = [message[i:i+2000] for i in range(0, len(message), 2000)]
            
            for message_part in message_parts:
                await interaction.followup.send(message_part, ephemeral=True)
            
            return

    # ギルドIDが見つからなかった場合
    await interaction.followup.send(not_found_message, ephemeral=True)


@client.tree.command(name="ng_setting", description="NGワードを発言したユーザーに付与するロールと通知を送るチャンネルを設定します")
async def ng_setting(interaction: Interaction, role: discord.Role, channel: discord.TextChannel):
    json_file = ng_path

    with open(json_file, "r", encoding="utf-8") as file:
        json_data = json.load(file)

    guild_id = interaction.guild_id  # コマンドを実行したギルドIDを取得

    # 対象のギルドIDが存在するかチェック、存在すればロールIDとチャンネルIDを更新
    found_guild = False  # ギルドIDが見つかったかどうかを示すフラグ

    for item in json_data:
        if item.get("GUILD_ID") == guild_id:
            item["ROLE_ID"] = role.id
            item["CHANNEL_ID"] = channel.id
            found_guild = True
            break

    # ギルドIDが見つからなかった場合、新たなデータを作成
    if not found_guild:
        new_data = {
            "GUILD_ID": guild_id,
            "ROLE_ID": role.id,
            "CHANNEL_ID": channel.id,
            "TARGET_MESSAGE": []
        }
        json_data.append(new_data)

    # 更新したJSONデータをファイルに書き込む
    with open(json_file, "w", encoding="utf-8") as file:
        json.dump(json_data, file, ensure_ascii=False, indent=4)

    await interaction.response.send_message(
        f"NGワードを発言したユーザーに付与するロールと、通知するチャンネルを更新しました。\nロール: {role.name}\nチャンネル: {channel.mention}",
        ephemeral=True
    )

#endregion

# 起動時に動作する処理 招待コードの内部処理在中
@client.event
async def on_ready():
    # コマンドの同期
    await client.setup_hook()
    # 起動したらターミナルにログイン通知が表示される
    print("SA-BOT2がログインしました")

# ユーザーがメッセージを送信した時の処理 NGワード対応の処理在中
@client.event
async def on_message(message):
    # ボットからのメッセージは無視
    if message.author == client.user:
        return
    
    json_file = ng_path
    content = message.content
    guild_id = message.guild.id

    with open(json_file, "r", encoding="utf-8") as file:
        json_data = json.load(file)

    # ギルドごとのNGワードリストに基づき、メッセージ内容がNGワードを含むかチェックします
    for item in json_data:
        if item.get("GUILD_ID") == guild_id:
            target_messages = item.get("TARGET_MESSAGE")

            # NGワードを含むメッセージの場合
            if any(target_message.get("CONTENT") in content for target_message in target_messages):
                # ユーザーのロールを一時的に保持する
                user_roles = message.author.roles.copy()
                
                await message.delete()
                
                # NGワードを発言したユーザーに付与するロールを取得します
                bad_user_role_id = item.get("ROLE_ID")
                bad_user_role = discord.utils.get(message.guild.roles, id=bad_user_role_id)
                
                for role in user_roles:
                    try:
                        # ユーザーのロールを剥奪する。everyoneは除外。
                        if role.name != "@everyone":
                            await message.author.remove_roles(role)
                    except discord.Forbidden:
                        print(f"Failed to remove role: {role.name}")

                # メッセージが削除される前のユーザーのロールを変数に入れる。
                role_names = ", ".join(role.name for role in user_roles if role.name != "@everyone")

                # NGワードを発言したユーザーに指定のロールを付与する
                await message.author.add_roles(bad_user_role)

                # メッセージが削除され、ロールが変更されたことを特定のチャンネルに通知する
                notify_channel_id = item.get("CHANNEL_ID")
                notify_channel = client.get_channel(notify_channel_id)
                await notify_channel.send(f"{message.author.mention}さん のメッセージにNGワードが含まれていたため削除しました。\n元々付与されていたロール：{role_names}\n\nメッセージ内容：{content}")
                break

# BOTを起動する処理　これより下あるものは実行されないので注意
client.run(TOKEN)
