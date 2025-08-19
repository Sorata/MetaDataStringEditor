using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace MetaDataStringEditor {

    public class EditorListItem : ListViewItem {

        public bool IsEdit { private set; get; }
        public byte[] OriginStrBytes { private set; get; }
        public byte[] NewStrBytes { private set; get; }
        private string currentSearchKeyword = "";

        public EditorListItem(byte[] OriginStrBytes) {
            this.OriginStrBytes = OriginStrBytes;
            IsEdit = false;

            Text = Encoding.UTF8.GetString(OriginStrBytes);
            SubItems.Add("");
            SubItems.Add("");
        }

        public void SetNewStr(string newString) {
            NewStrBytes = Encoding.UTF8.GetBytes(newString);
            IsEdit = !Equals(OriginStrBytes, NewStrBytes);

            SubItems[1].Text = IsEdit ? newString : "";
            SubItems[2].Text = IsEdit ? "*" : "";
        }

        public void Discard() {
            NewStrBytes = null;
            IsEdit = false;

            SubItems[1].Text = "";
            SubItems[2].Text = "";
        }

        public bool MatchKeyWord(string keyWord) {
            return Text.ToLower().Contains(keyWord.ToLower()) ||
                SubItems[0].Text.ToLower().Contains(keyWord.ToLower()) ||
                SubItems[1].Text.ToLower().Contains(keyWord.ToLower());
        }

        public void SetSearchHighlight(string keyword) {
            currentSearchKeyword = keyword;
            if (string.IsNullOrEmpty(keyword)) {
                // 清除高亮
                BackColor = SystemColors.Window;
                ForeColor = SystemColors.WindowText;
            } else if (MatchKeyWord(keyword)) {
                // 设置高亮背景色
                BackColor = Color.Yellow;
                ForeColor = Color.Black;
            } else {
                // 恢复默认颜色
                BackColor = SystemColors.Window;
                ForeColor = SystemColors.WindowText;
            }
        }

        public void SetSelectedHighlight(bool isSelected) {
            if (isSelected && !string.IsNullOrEmpty(currentSearchKeyword) && MatchKeyWord(currentSearchKeyword)) {
                // 当前选中的搜索结果使用更深的高亮色
                BackColor = Color.Orange;
                ForeColor = Color.Black;
            } else if (!string.IsNullOrEmpty(currentSearchKeyword) && MatchKeyWord(currentSearchKeyword)) {
                // 普通搜索结果高亮
                BackColor = Color.Yellow;
                ForeColor = Color.Black;
            } else {
                // 恢复默认颜色
                BackColor = SystemColors.Window;
                ForeColor = SystemColors.WindowText;
            }
        }
    }
}
