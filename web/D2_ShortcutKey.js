import { app } from "../../scripts/app.js";

const D2_SHORTCUT_DEFAULT_COMMENT = "ctrl+/";

/**
 * ショートカットキーを作るクラス
 */
class D2_ShortcutKeyControl {
  shortcutKeys = {
    comment: [],
  };

  constructor() {
    // 設定読み込み
    this.changeKeySetting("comment", app.ui.settings.getSettingValue("D2.shortcutKey.comment", D2_SHORTCUT_DEFAULT_COMMENT));

    // イベントハンドラをバインド
    this._onKeyDown = this._onKeyDown.bind(this);

    // キーボードイベントリスナーを設定
    document.addEventListener('keydown', this._onKeyDown);
  }

  /**
   * キーボードイベントハンドラ
   * @param {KeyboardEvent} e キーボードイベント
   */
  _onKeyDown(e) {
    // アクティブな要素がテキストエリアでない場合は処理しない
    if (!(document.activeElement instanceof HTMLTextAreaElement)) {
      return;
    }

    // 押されたキーの配列を取得
    const pressedKeys = this._getPressedKeys(e);
    
    // コメント
    if (this.shortcutKeys.comment.length > 0 && 
        this._compareKeyArrays(pressedKeys, this.shortcutKeys.comment)) {
      e.preventDefault();
      this.comment();
      return;
    }
  }

  /**
   * キーボードイベントから押されたキーの配列を生成
   * @param {KeyboardEvent} e キーボードイベント
   * @returns {string[]} 押されたキーの配列
   */
  _getPressedKeys(e) {
    const keys = [];
    if (e.ctrlKey) keys.push('ctrl');
    if (e.altKey) keys.push('alt');
    if (e.shiftKey) keys.push('shift');
    if (e.metaKey) keys.push('meta');
    
    // キーコードを追加（特殊キーの場合は名前、それ以外は小文字）
    let key = e.key.toLowerCase();
    if (key === ' ') key = 'space';
    if (key === '/') key = '/';
    if (key.length === 1 || ['enter', 'tab', 'space', 'backspace', 'delete', 'escape', 'arrowup', 'arrowdown', 'arrowleft', 'arrowright'].includes(key)) {
      keys.push(key);
    }
    
    return keys;
  }

  /**
   * 2つのキー配列が同じ要素を含むか比較
   * @param {string[]} arr1 キー配列1
   * @param {string[]} arr2 キー配列2
   * @returns {boolean} 同じ要素を含む場合はtrue
   */
  _compareKeyArrays(arr1, arr2) {
    if (arr1.length !== arr2.length) return false;
    
    // 配列をソートしてから比較
    const sorted1 = [...arr1].sort();
    const sorted2 = [...arr2].sort();
    
    return sorted1.every((key, index) => key === sorted2[index]);
  }

  /**
   * ショートカットキー設定を変更
   */
  changeKeySetting(param, value) {
    this.shortcutKeys[param] = value ? value.toLowerCase().split('+').map(k => k.trim()).filter(k => k) : [];
  }

  /**
   * コメント処理
   * 選択範囲がない場合：
   * 1. マルチラインコメントの探索を行い、存在するなら削除
   * 2. 行頭にシングルラインコメントがあれば削除
   * 3. シングルラインコメントを付与
   * 選択範囲がある場合：
   * - マルチラインコメントを付与
   */
  comment() {
    const textarea = document.activeElement;
    if (!(textarea instanceof HTMLTextAreaElement)) {
      return;
    }

    const text = textarea.value;
    const selStart = textarea.selectionStart;
    const selEnd = textarea.selectionEnd;
    
    // 選択範囲があるかどうか
    const hasSelection = selStart !== selEnd;
    
    let newText;
    let newSelStart;
    let newSelEnd;
    
    if (hasSelection) {
      // 選択範囲がある場合は /* */ を付与
      const selectedText = text.substring(selStart, selEnd);
      const beforeText = text.substring(0, selStart);
      const afterText = text.substring(selEnd);
      
      newText = beforeText + '/*' + selectedText + '*/' + afterText;
      // 選択範囲を解除し、/* の後ろにカーソルを移動
      newSelStart = selStart + 2;
      newSelEnd = selStart + 2;
    } else {
      // 選択範囲がない場合
      
      // 1. /* */ の探索
      const beforeText = text.substring(0, selStart);
      const afterText = text.substring(selEnd);
      const lastCommentStartPos = beforeText.lastIndexOf('/*');
      const firstCommentEndPos = afterText.indexOf('*/');
      
      if (lastCommentStartPos !== -1 && firstCommentEndPos !== -1) {
        // /* */ が見つかった場合、コメント部分を削除して内容を保持
        const commentStartPos = lastCommentStartPos;
        const commentEndPos = selEnd + firstCommentEndPos + 2; // +2 for '*/'
        const commentContent = text.substring(commentStartPos + 2, commentEndPos - 2);
        
        newText = text.substring(0, commentStartPos) + commentContent + text.substring(commentEndPos);
        newSelStart = commentStartPos;
        newSelEnd = commentStartPos;
      } else {
        // 2. & 3. 行コメントの処理
        
        // 現在のカーソル位置を含む行の開始位置と終了位置を取得
        let lineStart = text.lastIndexOf('\n', selStart - 1) + 1;
        let lineEnd = text.indexOf('\n', selStart);
        if (lineEnd === -1) lineEnd = text.length;
        
        // 現在の行のテキストを取得
        const line = text.substring(lineStart, lineEnd);
        
        // 行頭に「//」があるかチェック
        const hasComment = line.startsWith('//');
        
        // 新しい行のテキスト
        let newLine;
        if (hasComment) {
          // コメントを削除
          newLine = line.substring(2).trimStart();
        } else {
          // コメントを追加
          newLine = '// ' + line;
        }
        
        // テキストエリアの内容を更新
        newText = text.substring(0, lineStart) + newLine + text.substring(lineEnd);
        
        // カーソル位置を調整（選択範囲を解除）
        if (hasComment) {
          // コメントを削除した場合、カーソルを3文字前に移動
          newSelStart = selStart - 3;
          newSelEnd = newSelStart;
        } else {
          // コメントを追加した場合
          const cursorOffset = 3; // "// " の長さ
          newSelStart = selStart + cursorOffset;
          newSelEnd = newSelStart;
        }
      }
    }
    
    // テキストエリアの内容を更新
    textarea.value = newText;
    
    // 選択範囲を調整
    textarea.selectionStart = newSelStart;
    textarea.selectionEnd = newSelEnd;
    
    // 変更イベントを発火
    textarea.dispatchEvent(new Event('input', { bubbles: true }));
  }
}


(function () {
  const shortcutKeyControl = new D2_ShortcutKeyControl();

  app.ui.settings.addSetting({
    id: "D2.shortcutKey.comment",
    name: `Comment (default: ${D2_SHORTCUT_DEFAULT_COMMENT})`,
    type: "string",
    defaultValue: D2_SHORTCUT_DEFAULT_COMMENT,
    onChange(value) {
      shortcutKeyControl.changeKeySetting("comment", value);
    },
  });
})();
