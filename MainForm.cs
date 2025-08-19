using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading;
using System.Windows.Forms;

namespace MetaDataStringEditor {
    public partial class MainForm : Form {
        public MainForm() {
            InitializeComponent();

            Logger.LogAction += delegate (string msg) {
                if (InvokeRequired) {
                    Invoke(new Action(delegate { toolStripStatusLabel1.Text = msg; }));
                } else {
                    toolStripStatusLabel1.Text = msg;
                }
            };

            ProgressBar.SetMaxAction += delegate (int max) {
                if (InvokeRequired) {
                    Invoke(new Action(delegate {
                        toolStripProgressBar1.Maximum = max;
                        toolStripProgressBar1.Value = 0;
                    }));
                } else {
                    toolStripProgressBar1.Maximum = max;
                    toolStripProgressBar1.Value = 0;
                }
            };

            ProgressBar.PlusOneAction += delegate {
                if (InvokeRequired) {
                    Invoke(new Action(delegate { toolStripProgressBar1.Value++; }));
                } else {
                    toolStripProgressBar1.Value++;
                }
            };

            ProgressBar.ReportAction += delegate (int val) {
                if (InvokeRequired) {
                    Invoke(new Action(delegate { toolStripProgressBar1.Value = val; }));
                } else {
                    toolStripProgressBar1.Value = val;
                }
            };
            
            // 设置搜索框提示文本
            SetSearchBoxPlaceholder();
        }

        private FormStatus status = FormStatus.Waiting;
        private MetadataFile file;
        private EditForm editForm = new EditForm();
        private List<int> searchResults = new List<int>();
        private int currentSearchIndex = -1;
        private string lastSearchKeyword = "";

        // 菜单栏
        private void 加载ToolStripMenuItem_Click(object sender, EventArgs e) {
            if (status == FormStatus.Loading || status == FormStatus.Saving) {
                Logger.E("后台操作进行中");
                return;
            }

            if (openFileDialog1.ShowDialog(this) == DialogResult.OK) {
                status = FormStatus.Loading;
                ClearForm();
                ThreadPool.QueueUserWorkItem(delegate {
                    try {
                        file = new MetadataFile(openFileDialog1.FileName);
                        Invoke(new Action(delegate { Text = openFileDialog1.FileName; }));
                        Invoke(new Action(RefreshListView));
                        status = FormStatus.Editing;
                        Logger.I("加载完成");
                    } catch (Exception ex) {
                        Logger.E(ex.ToString());
                        file?.Dispose();
                        file = null;
                        status = FormStatus.Waiting;
                    }
                });
            }
        }

        private void RefreshListView() {
            Logger.I("刷新列表");

            listView1.BeginUpdate();
            for (int i = 0; i < file.strBytes.Count; i++) {
                EditorListItem item = new EditorListItem(file.strBytes[i]) {
                    Tag = i
                };
                listView1.Items.Add(item);
            }
            listView1.EndUpdate();
        }

        private void 另存为ToolStripMenuItem_Click(object sender, EventArgs e) {
            if (status != FormStatus.Editing) {
                Logger.E("状态错误");
                return;
            }

            if (saveFileDialog1.ShowDialog(this) == DialogResult.OK) {
                status = FormStatus.Saving;
                
                ThreadPool.QueueUserWorkItem(delegate {
                    file.WriteToNewFile(saveFileDialog1.FileName);
                    status = FormStatus.Editing;
                });
            }
        }

        private void 关闭文件ToolStripMenuItem_Click(object sender, EventArgs e) {
            ClearForm();
            status = FormStatus.Waiting;
        }
        
        // 搜索
        private void button1_Click(object sender, EventArgs e) {
            if (textBox1.Text.Length > 0)
                SearchToNext();
        }

        private void buttonPrevious_Click(object sender, EventArgs e) {
            if (textBox1.Text.Length > 0)
                SearchToPrevious();
        }

        private void textBox1_KeyPress(object sender, KeyPressEventArgs e) {
            if (e.KeyChar == '\r' && textBox1.Text.Length > 0)
                SearchToNext();
        }

        protected override bool ProcessCmdKey(ref Message msg, Keys keyData) {
            // 处理快捷键
            switch (keyData) {
                case Keys.Control | Keys.F:
                    // Ctrl+F: 聚焦到搜索框
                    textBox1.Focus();
                    textBox1.SelectAll();
                    return true;
                    
                case Keys.F3:
                    // F3: 查找下一个
                    if (textBox1.Text.Length > 0) {
                        SearchToNext();
                    }
                    return true;
                    
                case Keys.Shift | Keys.F3:
                    // Shift+F3: 查找上一个
                    if (textBox1.Text.Length > 0) {
                        SearchToPrevious();
                    }
                    return true;
                    
                case Keys.Escape:
                    // Esc: 清除搜索
                    if (textBox1.Focused) {
                        textBox1.Text = "";
                        listView1.Focus();
                    }
                    return true;
            }
            
            return base.ProcessCmdKey(ref msg, keyData);
        }

        private void textBox1_TextChanged(object sender, EventArgs e) {
            // 忽略提示文本
            if (textBox1.Text == "输入搜索内容... (Ctrl+F)") {
                return;
            }
            
            // 当搜索文本改变时，重置搜索状态并更新计数显示
            string keyWord = textBox1.Text.Trim();
            if (keyWord != lastSearchKeyword) {
                searchResults.Clear();
                currentSearchIndex = -1;
                lastSearchKeyword = keyWord;
                
                // 更新所有项的高亮显示
                for (int i = 0; i < listView1.Items.Count; i++) {
                    var item = listView1.Items[i] as EditorListItem;
                    item.SetSearchHighlight(keyWord);
                    if (!string.IsNullOrEmpty(keyWord) && item.MatchKeyWord(keyWord)) {
                        searchResults.Add(i);
                    }
                }
                
                UpdateSearchCountDisplay();
            }
        }

        private void PerformSearch() {
            string keyWord = textBox1.Text.Trim();
            if (string.IsNullOrEmpty(keyWord)) {
                searchResults.Clear();
                currentSearchIndex = -1;
                UpdateSearchCountDisplay();
                return;
            }

            // 如果搜索关键词改变了，重新搜索
            if (keyWord != lastSearchKeyword) {
                searchResults.Clear();
                currentSearchIndex = -1;
                lastSearchKeyword = keyWord;

                // 查找所有匹配的项
                for (int i = 0; i < listView1.Items.Count; i++) {
                    var item = listView1.Items[i] as EditorListItem;
                    if (item.MatchKeyWord(keyWord)) {
                        searchResults.Add(i);
                    }
                }
            }

            UpdateSearchCountDisplay();
        }

        private void SearchToNext() {
            PerformSearch();
            if (searchResults.Count == 0) {
                Logger.I("找不到搜索字符串");
                return;
            }

            currentSearchIndex = (currentSearchIndex + 1) % searchResults.Count;
            NavigateToSearchResult();
        }

        private void SearchToPrevious() {
            PerformSearch();
            if (searchResults.Count == 0) {
                Logger.I("找不到搜索字符串");
                return;
            }

            currentSearchIndex = currentSearchIndex <= 0 ? searchResults.Count - 1 : currentSearchIndex - 1;
            NavigateToSearchResult();
        }

        private void NavigateToSearchResult() {
            if (currentSearchIndex >= 0 && currentSearchIndex < searchResults.Count) {
                // 清除之前的选中状态和高亮
                foreach (ListViewItem item in listView1.Items) {
                    item.Selected = false;
                    var editorItem = item as EditorListItem;
                    editorItem.SetSelectedHighlight(false);
                }
                
                int itemIndex = searchResults[currentSearchIndex];
                var selectedItem = listView1.Items[itemIndex] as EditorListItem;
                selectedItem.Selected = true;
                selectedItem.SetSelectedHighlight(true);
                selectedItem.EnsureVisible();
                listView1.Focus();
                UpdateSearchCountDisplay();
            }
        }

        private void UpdateSearchCountDisplay() {
            if (string.IsNullOrEmpty(textBox1.Text.Trim())) {
                labelSearchCount.Text = "";
            } else if (searchResults.Count == 0) {
                labelSearchCount.Text = "0/0";
            } else {
                labelSearchCount.Text = $"{currentSearchIndex + 1}/{searchResults.Count}";
            }
        }
        
        private void SetSearchBoxPlaceholder() {
            // 为搜索框添加水印提示
            if (string.IsNullOrEmpty(textBox1.Text)) {
                textBox1.ForeColor = Color.Gray;
                textBox1.Text = "输入搜索内容... (Ctrl+F)";
            }
        }
        
        private void textBox1_Enter(object sender, EventArgs e) {
            // 当搜索框获得焦点时，清除提示文本
            if (textBox1.Text == "输入搜索内容... (Ctrl+F)") {
                textBox1.Text = "";
                textBox1.ForeColor = Color.Black;
            }
        }
        
        private void textBox1_Leave(object sender, EventArgs e) {
            // 当搜索框失去焦点且为空时，显示提示文本
            if (string.IsNullOrEmpty(textBox1.Text)) {
                SetSearchBoxPlaceholder();
            }
        }

        // 修改

        private void ListView1_MouseClick(object sender, MouseEventArgs e)
        {
            var item = listView1.GetItemAt(e.X, e.Y);
            if (item != null)
            {
                item.Selected = true;
                contextMenuStrip1.Show(listView1, e.Location);
            }
        }

        private void listView1_MouseDoubleClick(object sender, MouseEventArgs e) {
            var item = listView1.SelectedItems[0] as EditorListItem;
            startEditor(item);
        }


        private void 编辑ToolStripMenuItem_Click(object sender, EventArgs e)
        {
            var item = listView1.SelectedItems[0] as EditorListItem;
            startEditor(item);
        }

        private void startEditor(EditorListItem item)
        {
            editForm.ShowDialog(this, item);
            if (item.IsEdit)
                file.strBytes[(int)item.Tag] = item.NewStrBytes;
            else
                file.strBytes[(int)item.Tag] = item.OriginStrBytes;
        }

        // 通用
        private void ClearForm() {
            listView1.Items.Clear();
            file?.Dispose();
            file = null;
            Text = "MetadataStringEditor";
            // 重置搜索状态
            searchResults.Clear();
            currentSearchIndex = -1;
            lastSearchKeyword = "";
            textBox1.Text = "";
            SetSearchBoxPlaceholder();
            UpdateSearchCountDisplay();
        }

        private enum FormStatus { Waiting, Loading, Saving, Editing }

    }

    public static class Logger {
        public static Action<string> LogAction;

        private static void Log(string level, string msg) {
            LogAction($"[{level}] {msg}");
        }

        public static void D(string msg) { Log("debug", msg); }
        public static void I(string msg) { Log("info", msg); }
        public static void E(string msg) { Log("error", msg); }
    }

    public static class ProgressBar {
        public static Action<int> SetMaxAction;
        public static Action PlusOneAction;
        public static Action<int> ReportAction;

        public static void SetMax(int max) => SetMaxAction(max);
        public static void Report(int val) => ReportAction(val);
        public static void Report() => PlusOneAction();
    }

}
