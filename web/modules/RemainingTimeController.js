
/**
 * ComfyUIのキュー実行における残り時間を推定し、指定されたウィジェットに表示するためのコントローラークラスです。
 * 実行中のタスクの経過時間と進捗状況から、全体の完了までの残り時間を計算し、
 * hh:mm:ss 形式で表示を更新します。
 */
class RemainingTimeController {
    INIT_TIME = "00:00";


    constructor(remainingTimeWidget) {
        this.remainingTimeWidget = remainingTimeWidget;
        this._resetStartTime();
        this.intervalId = 0;
    }

    /**
     * 残り時間を計算して表示をアップデートする
     * @param {int} index 現在の実行回数
     * @param {int} total トータル実行回数
     */
    calculateRemainingTime(index, total) {
        if (this.startTime === 0) {
            // 現在のUnixTimeを登録
            this.startTime = Date.now();
            this.remainingTimeWidget.setValue(RemainingTimeController.INIT_TIME);
        } else {
            // 経過時間、現在回数(index)、トータル回数(total)から推定残り時間を計算
            // 直前までの作業について計算なので index はそのまま
            const elapsed = Date.now() - this.startTime;
            const avgTimePerItem = elapsed / index;
            const remainingItems = total - index;
            this.remainingTime = Math.floor(avgTimePerItem * remainingItems);
            this._updateRemainingTime();
            this._countDown();
        }
    }

    // 開始時刻、残り時間をリセット
    _resetStartTime() {
        this.startTime = 0;
        this.remainingTime = 0;
    }
    
    // Unixタイムを hh:mm:ss に変換して表示
    _updateRemainingTime() {
        const timeStr = RemainingTimeController.convertTime(this.remainingTime);
        this.remainingTimeWidget.setValue(timeStr);
    }

    // カウントダウン
    // 0秒以下になったら停止
    // 残りキュー数が0になっても停止
    _countDown() {
        clearInterval(this.intervalId);

        this.intervalId = setInterval(() => {
            this.remainingTime = Math.max(0, this.remainingTime - 1000);

            if (this.remainingTime <= 0 || app.ui.lastQueueSize <= 0) {
                this._resetStartTime();
                clearInterval(this.intervalId);
            }

            this._updateRemainingTime();
        }, 1000);
    }

    static convertTime(time) {
        const hours = Math.floor(time / (1000 * 60 * 60));
        const minutes = Math.floor((time % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((time % (1000 * 60)) / 1000);
        const timeStr = `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}:${seconds
            .toString()
            .padStart(2, "0")}`;
        return timeStr;
    }
}

export { RemainingTimeController }

