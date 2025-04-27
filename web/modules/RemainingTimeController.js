
/**
 * ComfyUIのキュー実行における残り時間を推定し、指定されたウィジェットに表示するためのコントローラークラスです。
 * 実行中のタスクの経過時間と進捗状況から、全体の完了までの残り時間を計算し、
 * hh:mm:ss 形式で表示を更新します。
 */
class RemainingTimeController {

    constructor(timeWidget) {
        this.timeWidget = timeWidget;
        this.intervalId = 0;
        this.startTime = 0;
    }

    /**
     * 実行回数を残り時間を計算して表示をアップデートする
     * @param {int} index 現在の実行回数
     * @param {int} total トータル実行回数
     */
    setTimeWithCount(index, total) {
        if (this.startTime === 0) {
            // 現在のUnixTimeを登録
            this.startTime = Date.now();
            this.timeWidget.setValue(0);
        } else {
            // 経過時間、現在回数(index)、トータル回数(total)から推定残り時間を計算
            // 直前までの作業について計算なので index はそのまま
            const elapsed = Date.now() - this.startTime;
            const avgTimePerItem = elapsed / index;
            const remainingItems = total - index;
            const remainingTime = Math.floor(avgTimePerItem * remainingItems);
            this.setRemainingTime(remainingTime);
        }
    }

        /**
     * 実行回数を残り時間を計算して表示をアップデートする
     * @param {int} time 残り時間のミリ秒
     */
    setRemainingTime(time) {
        this.timeWidget.setValue(time);
        this._countDown();
    }
    
    // 開始時刻、残り時間をリセット
    _resetStartTime() {
        this.startTime = 0;
        this.remainingTime = 0;
    }
    
    // カウントダウン
    // 0秒以下になったら停止
    // 残りキュー数が0になっても停止
    _countDown() {
        clearInterval(this.intervalId);

        this.intervalId = setInterval(() => {
            let remainingTime = this.timeWidget.value;
            remainingTime = Math.max(0, remainingTime - 1000);

            if (remainingTime <= 0 || app.ui.lastQueueSize <= 0) {
                this._resetStartTime();
                clearInterval(this.intervalId);
            }

            this.timeWidget.setValue(remainingTime);
        }, 1000);
    }
}

export { RemainingTimeController }

