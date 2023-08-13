using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using WMPLib;

namespace オセロ
{
    public partial class Form1 : Form
    {
        //左上の余白
        Point leftTopPoint = new Point(30, 30);

        Stone[,] StonePosition = new Stone[8, 8];

        Music music = new Music();

        bool isYour = true;
        bool player = true;

        public Form1()
        {
            InitializeComponent();

            CreatePictureBoxes();

            GameStart();
        }
        void CreatePictureBoxes()
        {
            for (int row = 0; row < 8; row++)
            {
                for (int colum = 0; colum < 8; colum++)
                {
                    Stone stone = new Stone(colum, row);
                    stone.Parent = this;
                    stone.Size = new Size(40, 40);
                    stone.BorderStyle = BorderStyle.FixedSingle;
                    stone.Location = new Point(leftTopPoint.X + colum * 40, leftTopPoint.Y + row * 40);
                    StonePosition[colum, row] = stone;
                    stone.StoneClick += Box_PictureBoxExClick;
                    stone.BackColor = Color.Green;
                }
            }
        }

        void GameStart()
        {
            var stones = StonePosition.Cast<Stone>();
            foreach (Stone stone in stones)
                stone.StoneColor = StoneColor.None;

            for (int row = 0; row < 8; row++)
            {
                for (int colum = 0; colum < 8; colum++)
                {
                    StonePosition[colum, row].StoneColor = StoneColor.None;
                }
            }

            StonePosition[3, 3].StoneColor = StoneColor.Black;
            StonePosition[4, 4].StoneColor = StoneColor.Black;

            StonePosition[3, 4].StoneColor = StoneColor.White;
            StonePosition[4, 3].StoneColor = StoneColor.White;

            isYour = true;

            toolStripStatusLabel1.Text = "黒の手番です";

        }

        private void startToolStripMenuItem_Click(object sender, EventArgs e)
        {
        }

        private void pictureBox1_Click(int x, int y)
        {              
        }

        async private void Box_PictureBoxExClick(int x, int y)
        {
            if (player)
            {
                if (isYour)
                {
                    // 着手可能な場所か調べる
                    List<Stone> stones = GetRevarseStones(x, y, StoneColor.Black);

                    var Color = StonePosition[x, y].StoneColor;

                    if (Color == StoneColor.None)
                    {
                        // 着手可能であれば石を置き、挟んだ石をひっくり返す
                        if (stones.Count != 0)
                        {
                            StonePosition[x, y].StoneColor = StoneColor.Black;
                            stones.Select(xx => xx.StoneColor = StoneColor.Black).ToList();
                            isYour = false;

                            toolStripStatusLabel1.Text = ("白の手番です");

                            GameSetCheck();

                            await Task.Delay(1000);

                            //EnemyThink();
                            return;
                        }
                    }
                    else
                    {
                        toolStripStatusLabel1.Text = ("そこには置けません、黒の手番です");
                    }
                }
                else if (!isYour)
                {

                    List<Stone> stones = GetRevarseStones(x, y, StoneColor.White);

                    var Color = StonePosition[x, y].StoneColor;

                    if (Color == StoneColor.None)
                    {
                        // 着手可能であれば石を置き、挟んだ石をひっくり返す
                        if (stones.Count != 0)
                        {
                            StonePosition[x, y].StoneColor = StoneColor.White;
                            stones.Select(xx => xx.StoneColor = StoneColor.White).ToList();
                            isYour = true;

                            toolStripStatusLabel1.Text = ("黒の手番です");

                            GameSetCheck();

                            await Task.Delay(1000);



                            //EnemyThink();
                            return;
                        }
                    }
                    else
                    {
                        toolStripStatusLabel1.Text = ("そこには置けません、白の手番です");
                    }
                }
            }
            else
            {
                if (isYour)
                {
                    // 着手可能な場所か調べる
                    List<Stone> stones = GetRevarseStones(x, y, StoneColor.Black);

                    var Color = StonePosition[x, y].StoneColor;

                    if (Color == StoneColor.None)
                    {
                        // 着手可能であれば石を置き、挟んだ石をひっくり返す
                        if (stones.Count != 0)
                        {
                            StonePosition[x, y].StoneColor = StoneColor.Black;
                            stones.Select(xx => xx.StoneColor = StoneColor.Black).ToList();
                            isYour = false;

                            toolStripStatusLabel1.Text = ("コンピューターの手番です");

                            await Task.Delay(1000);

                            EnemyThink();
                            return;
                        }
                    }
                    else
                    {
                        toolStripStatusLabel1.Text = ("そこには置けません、あなたの手番です");
                    }
                }
            }
        }
        
        void GameSetCheck()
        {
            var stones = StonePosition.Cast<Stone>();                    

            var Bhands = stones.ToList();
            int Bcount = Bhands.Count();

            // 黒の手は存在するのか確認
            stones = StonePosition.Cast<Stone>();
            stones = stones.Where(xx => xx.StoneColor == StoneColor.None && GetRevarseStones(xx.Colum, xx.Row, StoneColor.Black).Any());
            Bhands = stones.ToList();
            Bcount = Bhands.Count();

            var Whands = stones.ToList();
            int Wcount = Bhands.Count();

            // 白の手は存在するのか確認
            stones = StonePosition.Cast<Stone>();
            stones = stones.Where(xx => xx.StoneColor == StoneColor.None && GetRevarseStones(xx.Colum, xx.Row, StoneColor.White).Any());
            Whands = stones.ToList();
            Wcount = Whands.Count();

            // 「手」が存在するならプレーヤーの手番とする
            if (Bcount == 0 && Wcount == 0)
            {
                OnGameset();
            }
            else if(Bcount == 0 && isYour)
            {
                toolStripStatusLabel1.Text = "黒はパスしました。白の手番です。";
                isYour = false;
                return;
            }
            else if(Wcount == 0 && !isYour)
            {
                toolStripStatusLabel1.Text = "白はパスしました。黒の手番です。";
                isYour = true;
                return;
            }
            else
            {
                return;
            }
        }
                
        void EnemyThink()
        {
            toolStripStatusLabel1.Text = "コンピュータが考えています";

            bool isComPassed = false;
            bool isYouPassed = false;
            while (true)
            {
                // Cast メソッドで 1次元に
                var stones = StonePosition.Cast<Stone>();

                // 石が置かれていない場所で挟むことができる場所を探す。
                stones = stones.Where(xx => xx.StoneColor == StoneColor.None && GetRevarseStones(xx.Colum, xx.Row, StoneColor.White).Any());
                var hands = stones.ToList();
                int count = hands.Count();
                if (count > 0)
                {
                    Random random = new Random();
                    // 石をおける場所が見つかったらそのなかから適当に次の手を選ぶ
                    Stone stone = hands[random.Next() % count];

                    // 石を置いてひっくり返す
                    StonePosition[stone.Colum, stone.Row].StoneColor = StoneColor.White;
                    List<Stone> stones1 = GetRevarseStones(stone.Colum, stone.Row, StoneColor.White);
                    stones1.Select(xx => xx.StoneColor = StoneColor.White).ToList();
                }
                else
                {
                    if (isYouPassed)
                    {
                        // 双方に「手」が存在しない場合はゲームセットとする
                        OnGameset();
                        return;
                    }

                    // 石をおける場所が見つからない場合はパス
                    isComPassed = true;
                }

                // プレイヤーの手番だが、「手」は存在するのか？
                stones = StonePosition.Cast<Stone>();
                stones = stones.Where(xx => xx.StoneColor == StoneColor.None && GetRevarseStones(xx.Colum, xx.Row, StoneColor.Black).Any());
                hands = stones.ToList();
                count = hands.Count();

                // 「手」が存在するならプレーヤーの手番とする
                if (count > 0)
                {
                    isYour = true;
                    if (isComPassed)
                        toolStripStatusLabel1.Text = "コンピュータはパスしました。あなたの手番です。";
                    else
                        toolStripStatusLabel1.Text = "あなたの手番です。";
                    return;
                }
                else
                {
                    // 「手」が存在しない場合はもう一度コンピュータの手番とする
                    if (!isComPassed)
                    {
                        isYouPassed = true;
                        toolStripStatusLabel1.Text = "あなたの手番ですが手がありません";
                    }
                    else
                    {
                        // 双方に「手」が存在しない場合はゲームセットとする                        
                        OnGameset();
                        return;
                    }
                }
            }
        }
        

        void OnGameset()
            {
                var stones = StonePosition.Cast<Stone>();

                int blackCount = stones.Count(xx => xx.StoneColor == StoneColor.Black);
                int whiteCount = stones.Count(xx => xx.StoneColor == StoneColor.White);

                music.SE();

                string str = "";
                if (blackCount != whiteCount)
                {
                    string winner = blackCount > whiteCount ? "黒" : "白";
                    str = String.Format("終局しました。{0} 対 {1} で {2} の勝ちです。", blackCount, whiteCount, winner);
                }
                else
                {
                    str = String.Format("終局しました。{0} 対 {1} で 引き分けです。", blackCount, whiteCount);
                }
                toolStripStatusLabel1.Text = str;
                return;
            }

            List<Stone> GetRevarseStones(int x, int y, StoneColor stoneColor)
            {
                List<Stone> stones = new List<Stone>();
                stones.AddRange(GetReverseOnPutUp(x, y, stoneColor)); // 上方向に挟めているものを取得
                stones.AddRange(GetReverseOnPutDown(x, y, stoneColor)); // 下
                stones.AddRange(GetReverseOnPutLeft(x, y, stoneColor)); // 左
                stones.AddRange(GetReverseOnPutRight(x, y, stoneColor)); // 右
                stones.AddRange(GetReverseOnPutLeftTop(x, y, stoneColor)); // 左上
                stones.AddRange(GetReverseOnPutLeftDown(x, y, stoneColor)); // 左下
                stones.AddRange(GetReverseOnPutRightTop(x, y, stoneColor)); // 右上
                stones.AddRange(GetReverseOnPutRightDown(x, y, stoneColor)); // 右下

                return stones;
            }
            List<Stone> GetReverseOnPutUp(int x, int y, StoneColor color)
            {
                List<Stone> stones = new List<Stone>();
                StoneColor EnemyColor = StoneColor.None;
                if (color == StoneColor.Black)
                    EnemyColor = StoneColor.White;
                else
                    EnemyColor = StoneColor.Black;

                if (y - 1 < 0)
                    return stones;

                var s = StonePosition[x, y - 1];
                if (s.StoneColor == color || s.StoneColor == StoneColor.None)
                    return stones;

                stones.Add(s);

                for (int i = 0; ; i++)
                {
                    if (y - 1 - i < 0)
                        return new List<Stone>();

                    var s1 = StonePosition[x, y - 1 - i];
                    if (s1.StoneColor == EnemyColor)
                    {
                        stones.Add(s1);
                        continue;
                    }
                    if (s1.StoneColor == color)
                        return stones;
                    if (s1.StoneColor == StoneColor.None)
                        return new List<Stone>();
                }
            }

            List<Stone> GetReverseOnPutDown(int x, int y, StoneColor color)
            {
                List<Stone> stones = new List<Stone>();
                StoneColor enemyColor = StoneColor.None;
                if (color == StoneColor.Black)
                    enemyColor = StoneColor.White;
                else
                    enemyColor = StoneColor.Black;

                if (y + 1 > 7)
                    return stones;

                var s = StonePosition[x, y + 1];
                if (s.StoneColor == color || s.StoneColor == StoneColor.None)
                    return stones;

                stones.Add(s);

                for (int i = 0; ; i++)
                {
                    if (y + 1 + i > 7)
                        return new List<Stone>();

                    var s1 = StonePosition[x, y + 1 + i];
                    if (s1.StoneColor == enemyColor)
                    {
                        stones.Add(s1);
                        continue;
                    }
                    if (s1.StoneColor == color)
                        return stones;
                    if (s1.StoneColor == StoneColor.None)
                        return new List<Stone>();
                }
            }

            List<Stone> GetReverseOnPutLeft(int x, int y, StoneColor color)
            {
                List<Stone> stones = new List<Stone>();
                StoneColor enemyColor = StoneColor.None;
                if (color == StoneColor.Black)
                    enemyColor = StoneColor.White;
                else
                    enemyColor = StoneColor.Black;

                if (x - 1 < 0)
                    return stones;

                var s = StonePosition[x - 1, y];
                if (s.StoneColor == color || s.StoneColor == StoneColor.None)
                    return stones;

                stones.Add(s);

                for (int i = 0; ; i++)
                {
                    if (x - 1 - i < 0)
                        return new List<Stone>();

                    var s1 = StonePosition[x - 1 - i, y];
                    if (s1.StoneColor == enemyColor)
                    {
                        stones.Add(s1);
                        continue;
                    }
                    if (s1.StoneColor == color)
                        return stones;
                    if (s1.StoneColor == StoneColor.None)
                        return new List<Stone>();
                }
            }

            List<Stone> GetReverseOnPutRight(int x, int y, StoneColor color)
            {
                List<Stone> stones = new List<Stone>();
                StoneColor enemyColor = StoneColor.None;
                if (color == StoneColor.Black)
                    enemyColor = StoneColor.White;
                else
                    enemyColor = StoneColor.Black;

                if (x + 1 > 7)
                    return stones;

                var s = StonePosition[x + 1, y];
                if (s.StoneColor == color || s.StoneColor == StoneColor.None)
                    return stones;

                stones.Add(s);

                for (int i = 0; ; i++)
                {
                    if (x + 1 + i > 7)
                        return new List<Stone>();

                    var s1 = StonePosition[x + 1 + i, y];
                    if (s1.StoneColor == enemyColor)
                    {
                        stones.Add(s1);
                        continue;
                    }
                    if (s1.StoneColor == color)
                        return stones;
                    if (s1.StoneColor == StoneColor.None)
                        return new List<Stone>();
                }
            }

            List<Stone> GetReverseOnPutLeftTop(int x, int y, StoneColor color)
            {
                List<Stone> stones = new List<Stone>();
                StoneColor enemyColor = StoneColor.None;
                if (color == StoneColor.Black)
                    enemyColor = StoneColor.White;
                else
                    enemyColor = StoneColor.Black;

                if (x - 1 < 0)
                    return stones;
                if (y - 1 < 0)
                    return stones;

                var s = StonePosition[x - 1, y - 1];
                if (s.StoneColor == color || s.StoneColor == StoneColor.None)
                    return stones;

                stones.Add(s);

                for (int i = 0; ; i++)
                {
                    if (x - 1 - i < 0)
                        return new List<Stone>();

                    if (y - 1 - i < 0)
                        return new List<Stone>();

                    var s1 = StonePosition[x - 1 - i, y - 1 - i];
                    if (s1.StoneColor == enemyColor)
                    {
                        stones.Add(s1);
                        continue;
                    }
                    if (s1.StoneColor == color)
                        return stones;

                    if (s1.StoneColor == StoneColor.None)
                        return new List<Stone>();
                }
            }

            List<Stone> GetReverseOnPutRightTop(int x, int y, StoneColor color)
            {
                List<Stone> stones = new List<Stone>();
                StoneColor enemyColor = StoneColor.None;
                if (color == StoneColor.Black)
                    enemyColor = StoneColor.White;
                else
                    enemyColor = StoneColor.Black;

                if (x + 1 > 7)
                    return stones;
                if (y - 1 < 0)
                    return stones;

                var s = StonePosition[x + 1, y - 1];
                if (s.StoneColor == color || s.StoneColor == StoneColor.None)
                    return stones;

                stones.Add(s);

                for (int i = 0; ; i++)
                {
                    if (x + 1 + i > 7)
                        return new List<Stone>();

                    if (y - 1 - i < 0)
                        return new List<Stone>();

                    var s1 = StonePosition[x + 1 + i, y - 1 - i];
                    if (s1.StoneColor == enemyColor)
                    {
                        stones.Add(s1);
                        continue;
                    }
                    if (s1.StoneColor == color)
                        return stones;

                    if (s1.StoneColor == StoneColor.None)
                        return new List<Stone>();
                }
            }

            List<Stone> GetReverseOnPutRightDown(int x, int y, StoneColor color)
            {
                List<Stone> stones = new List<Stone>();
                StoneColor enemyColor = StoneColor.None;
                if (color == StoneColor.Black)
                    enemyColor = StoneColor.White;
                else
                    enemyColor = StoneColor.Black;

                if (x + 1 > 7)
                    return stones;
                if (y + 1 > 7)
                    return stones;

                var s = StonePosition[x + 1, y + 1];
                if (s.StoneColor == color || s.StoneColor == StoneColor.None)
                    return stones;

                stones.Add(s);

                for (int i = 0; ; i++)
                {
                    if (x + 1 + i > 7)
                        return new List<Stone>();

                    if (y + 1 + i > 7)
                        return new List<Stone>();

                    var s1 = StonePosition[x + 1 + i, y + 1 + i];
                    if (s1.StoneColor == enemyColor)
                    {
                        stones.Add(s1);
                        continue;
                    }
                    if (s1.StoneColor == color)
                        return stones;

                    if (s1.StoneColor == StoneColor.None)
                        return new List<Stone>();
                }
            }

            List<Stone> GetReverseOnPutLeftDown(int x, int y, StoneColor color)
            {
                List<Stone> stones = new List<Stone>();
                StoneColor enemyColor = StoneColor.None;
                if (color == StoneColor.Black)
                    enemyColor = StoneColor.White;
                else
                    enemyColor = StoneColor.Black;

                if (x - 1 < 0)
                    return stones;
                if (y + 1 > 7)
                    return stones;

                var s = StonePosition[x - 1, y + 1];
                if (s.StoneColor == color || s.StoneColor == StoneColor.None)
                    return stones;

                stones.Add(s);

                for (int i = 0; ; i++)
                {
                    if (x - 1 - i < 0)
                        return new List<Stone>();

                    if (y + 1 + i > 7)
                        return new List<Stone>();

                    var s1 = StonePosition[x - 1 - i, y + 1 + i];
                    if (s1.StoneColor == enemyColor)
                    {
                        stones.Add(s1);
                        continue;
                    }
                    if (s1.StoneColor == color)
                        return stones;

                    if (s1.StoneColor == StoneColor.None)
                        return new List<Stone>();
                }
            }

            private void Box_PictureBoxExClic(object sender, EventArgs e)
            {

            }

        private void Form1_Load(object sender, EventArgs e)
        {

        }

        private void 対戦ToolStripMenuItem_Click(object sender, EventArgs e)
        {
            player = true;
            GameStart();
        }

        private void cOM戦ToolStripMenuItem_Click(object sender, EventArgs e)
        {
            player = false;
            GameStart();

            toolStripStatusLabel1.Text = "あなたの手番です";
        }
        private void リセットToolStripMenuItem_Click(object sender, EventArgs e)
        {
            Application.Restart();
        }

        private void 音ToolStripMenuItem_Click(object sender, EventArgs e)
        {
            music.SE();
        }
    }

    public class Stone : PictureBox
        {
            StoneColor stoneColor = StoneColor.None;
            public int Colum
            {
                protected set;
                get;
            } = 0;
            public int Row
            {
                protected set;
                get;
            } = 0;

            public Stone(int colum, int row)
            {
                Colum = colum;
                Row = row;

                Click += Stone_Click;
            }

            public delegate void StoneClickHandler(int x, int y);
            public event StoneClickHandler StoneClick;
            private void Stone_Click(object sender, EventArgs e)
            {
                StoneClick?.Invoke(Colum, Row);
            }

            public StoneColor StoneColor
            {
                get { return stoneColor; }
                set
                {
                    stoneColor = value;

                    if (value == StoneColor.Black)
                        Image = Image.FromFile(@"black.png");
                    if (value == StoneColor.White)
                        Image = Image.FromFile(@"white.png");
                if (value == StoneColor.None)
                    Image = Image.FromFile(@"緑.png");
                }
            }
        }
        public enum StoneColor
        {
            None = 0,
            Black = 1,
            White = 2,
        }
    }




