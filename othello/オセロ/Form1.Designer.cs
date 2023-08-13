
namespace オセロ
{
    partial class Form1
    {
        /// <summary>
        /// 必要なデザイナー変数です。
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// 使用中のリソースをすべてクリーンアップします。
        /// </summary>
        /// <param name="disposing">マネージド リソースを破棄する場合は true を指定し、その他の場合は false を指定します。</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows フォーム デザイナーで生成されたコード

        /// <summary>
        /// デザイナー サポートに必要なメソッドです。このメソッドの内容を
        /// コード エディターで変更しないでください。
        /// </summary>
        private void InitializeComponent()
        {
            this.menuStrip1 = new System.Windows.Forms.MenuStrip();
            this.スタートToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.再開ToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.cOM戦ToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.リセットToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.statusStrip1 = new System.Windows.Forms.StatusStrip();
            this.toolStripStatusLabel1 = new System.Windows.Forms.ToolStripStatusLabel();
            this.menuStrip1.SuspendLayout();
            this.statusStrip1.SuspendLayout();
            this.SuspendLayout();
            // 
            // menuStrip1
            // 
            this.menuStrip1.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.スタートToolStripMenuItem});
            this.menuStrip1.Location = new System.Drawing.Point(0, 0);
            this.menuStrip1.Name = "menuStrip1";
            this.menuStrip1.Size = new System.Drawing.Size(377, 24);
            this.menuStrip1.TabIndex = 1;
            this.menuStrip1.Text = "menuStrip1";
            // 
            // スタートToolStripMenuItem
            // 
            this.スタートToolStripMenuItem.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.再開ToolStripMenuItem,
            this.cOM戦ToolStripMenuItem,
            this.リセットToolStripMenuItem});
            this.スタートToolStripMenuItem.Name = "スタートToolStripMenuItem";
            this.スタートToolStripMenuItem.Size = new System.Drawing.Size(53, 20);
            this.スタートToolStripMenuItem.Text = "スタート";
            // 
            // 再開ToolStripMenuItem
            // 
            this.再開ToolStripMenuItem.Name = "再開ToolStripMenuItem";
            this.再開ToolStripMenuItem.Size = new System.Drawing.Size(180, 22);
            this.再開ToolStripMenuItem.Text = "２人対戦";
            this.再開ToolStripMenuItem.Click += new System.EventHandler(this.対戦ToolStripMenuItem_Click);
            // 
            // cOM戦ToolStripMenuItem
            // 
            this.cOM戦ToolStripMenuItem.Name = "cOM戦ToolStripMenuItem";
            this.cOM戦ToolStripMenuItem.Size = new System.Drawing.Size(180, 22);
            this.cOM戦ToolStripMenuItem.Text = "COM戦";
            this.cOM戦ToolStripMenuItem.Click += new System.EventHandler(this.cOM戦ToolStripMenuItem_Click);
            // 
            // リセットToolStripMenuItem
            // 
            this.リセットToolStripMenuItem.Name = "リセットToolStripMenuItem";
            this.リセットToolStripMenuItem.Size = new System.Drawing.Size(180, 22);
            this.リセットToolStripMenuItem.Text = "リセット";
            this.リセットToolStripMenuItem.Click += new System.EventHandler(this.リセットToolStripMenuItem_Click);
            // 
            // statusStrip1
            // 
            this.statusStrip1.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.toolStripStatusLabel1});
            this.statusStrip1.Location = new System.Drawing.Point(0, 357);
            this.statusStrip1.Name = "statusStrip1";
            this.statusStrip1.Size = new System.Drawing.Size(377, 22);
            this.statusStrip1.TabIndex = 2;
            this.statusStrip1.Text = "statusStrip1";
            // 
            // toolStripStatusLabel1
            // 
            this.toolStripStatusLabel1.Name = "toolStripStatusLabel1";
            this.toolStripStatusLabel1.Size = new System.Drawing.Size(118, 17);
            this.toolStripStatusLabel1.Text = "toolStripStatusLabel1";
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 12F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(377, 379);
            this.Controls.Add(this.statusStrip1);
            this.Controls.Add(this.menuStrip1);
            this.MainMenuStrip = this.menuStrip1;
            this.Name = "Form1";
            this.Text = "Form1";
            this.Load += new System.EventHandler(this.Form1_Load);
            this.Click += new System.EventHandler(this.Box_PictureBoxExClic);
            this.menuStrip1.ResumeLayout(false);
            this.menuStrip1.PerformLayout();
            this.statusStrip1.ResumeLayout(false);
            this.statusStrip1.PerformLayout();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion
        private System.Windows.Forms.MenuStrip menuStrip1;
        private System.Windows.Forms.ToolStripMenuItem スタートToolStripMenuItem;
        private System.Windows.Forms.StatusStrip statusStrip1;
        private System.Windows.Forms.ToolStripStatusLabel toolStripStatusLabel1;
        private System.Windows.Forms.ToolStripMenuItem 再開ToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem cOM戦ToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem リセットToolStripMenuItem;
    }
}

