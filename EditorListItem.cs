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
        // 移除高亮功能相关字段

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
            if (string.IsNullOrEmpty(keyWord)) return false;
            
            // 使用不区分大小写的字符串比较，避免重复调用ToLower()
            return Text.IndexOf(keyWord, StringComparison.OrdinalIgnoreCase) >= 0 ||
                SubItems[0].Text.IndexOf(keyWord, StringComparison.OrdinalIgnoreCase) >= 0 ||
                SubItems[1].Text.IndexOf(keyWord, StringComparison.OrdinalIgnoreCase) >= 0;
        }

        // 移除高亮功能相关方法
    }
}
