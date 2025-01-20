import { app } from "/scripts/app.js";
import { sleep, findWidgetByName, getReadOnlyWidgetBase } from "./utils.js";

const REMAINING_INIT_TIME = "00:00:00";

/**
 * 残り時間計算
 */
class RemainingTimeController {

  constructor(remainingTimeWidget) {
    this.remainingTimeWidget = remainingTimeWidget;
    this.resetStartTime();
    this.intervalId = 0;
  }

  // 開始時刻、残り時間をリセット
  resetStartTime(){
    this.startTime = 0;
    this.remainingTime = 0;
  }

  // 残り時間を計算
  calculateRemainingTime(index, total){
    if(this.startTime === 0){
      // 現在のUnixTimeを登録
      this.startTime = Date.now();
      this.remainingTimeWidget.setValue(REMAINING_INIT_TIME);
    } else {
      // 経過時間、現在回数(index)、トータル回数(total)から推定残り時間を計算
      // 直前までの作業について計算なので index はそのまま
      const elapsed = Date.now() - this.startTime;
      const avgTimePerItem = elapsed / index;
      const remainingItems = total - index;
      this.remainingTime = Math.floor(avgTimePerItem * remainingItems);
      this.updateRemainingTime();
      this.countDown();
    }
  }

  // Unixタイムを hh:mm:ss に変換して表示
  updateRemainingTime(){
      const timeStr = RemainingTimeController.convertTime(this.remainingTime);
      this.remainingTimeWidget.setValue(timeStr);
  }

  // カウントダウン
  // 0秒以下になったら停止
  // 残りキュー数が0になっても停止
  countDown(){
    clearInterval(this.intervalId);

    this.intervalId = setInterval(()=>{
      this.remainingTime = Math.max(0, this.remainingTime - 1000);

      if(this.remainingTime <= 0 || app.ui.lastQueueSize <= 0){
        this.resetStartTime();
        clearInterval(this.intervalId);
      }

      this.updateRemainingTime();
    }, 1000);
  }

  static convertTime(time){
    const hours = Math.floor(time / (1000 * 60 * 60));
    const minutes = Math.floor((time % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((time % (1000 * 60)) / 1000);
    const timeStr = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    return timeStr;
  }
}



app.registerExtension({
  name: "Comfy.D2.D2_XY_Plot",

  async beforeRegisterNodeDef(nodeType, nodeData, app) {
    if (nodeData.name !== "D2 XY Plot" && nodeData.name !== "D2 XY Plot Easy") return;

    const origOnNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
        const r = origOnNodeCreated ? origOnNodeCreated.apply(this) : undefined;

        // なぜかラベルが書き換えられてしまうので戻す
        const autoQueueWidget = findWidgetByName(this, "auto_queue");
        autoQueueWidget.label = "auto_queue";

        const startIndexWidget = findWidgetByName(this, "start_index");
        startIndexWidget.label = "start_index";

        return r;
    };


    /**
     * ノード実行時
     */
    const onExecuted = nodeType.prototype.onExecuted;
    nodeType.prototype.onExecuted = async function (message) {
      onExecuted?.apply(this, arguments);

      const autoQueue = message["auto_queue"][0];
      const xArray = message["x_array"][0];
      const yArray = message["y_array"][0];
      const index = message["index"][0]; // 0スタート
      const total = message["total"][0];
      this.total = total;
      const indexWidget = findWidgetByName(this, "index");
     
      // 残り時間計算
      this.d2_remTimeController.calculateRemainingTime(index, total);

      // seed更新
      const seedWidget = findWidgetByName(this, "xy_seed");
      if(seedWidget){
        seedWidget.setValue(Math.floor(Math.random()*100000));
      }

      // まだ残りがあるならキューを入れる
      if(index + 1 < total && total >= 2){
        indexWidget.setValue(index + 1);

        if(autoQueue){
          await sleep(200);
          app.queuePrompt(0, 1);
        }
      }
      // 最後までいった
      else if(index + 1 >= total){
        indexWidget.setValue(0);
        // this.d2_remTimeController.resetStartTime();
      }
    };

  },

  getCustomWidgets(app) {
    return {
      D2_XYPLOT_RESET(node, inputName, inputData, app) {
        const widget = node.addWidget("button", "Set start index", "", () => {
          const startIndexWidget = findWidgetByName(node, "start_index");
          const indexWidget = findWidgetByName(node, "index");
          indexWidget.setValue(startIndexWidget.value);
        });
        // node.addCustomWidget(widget);
        // return widget;
      },

      D2_XYPLOT_INDEX(node, inputName, inputData, app) {
        const widget = getReadOnlyWidgetBase(node, "D2_XYPLOT_INDEX", inputName, 0);
        node.total = 0;

        widget.draw = function(ctx, node, width, y) {
          const text = `Index: ${this.value} / ${node.total}`;
          ctx.fillStyle = "#ffffff";
          ctx.font = "12px Arial";
          ctx.fillText(text, 20, y + 20);
        };
        node.addCustomWidget(widget);
        // return widget;
      },

      D2_XYPLOT_SEED(node, inputName, inputData, app) {
        const widget = getReadOnlyWidgetBase(node, "D2_XYPLOT_SEED", inputName, 0);

        widget.draw = function(ctx, node, width, y) {
          const text = `Seed: ${this.value}`;
          ctx.fillStyle = "#ffffff";
          ctx.font = "12px Arial";
          ctx.fillText(text, 20, y + 20);
        };
        node.addCustomWidget(widget);
        // return widget;
      },

      D2_XYPLOT_REMAINING_TIME(node, inputName, inputData, app) {
        const widget = getReadOnlyWidgetBase(node, "D2_XYPLOT_REMAINING_TIME", inputName, REMAINING_INIT_TIME);
        node.d2_remTimeController = new RemainingTimeController(widget);

        widget.draw = function(ctx, node, width, y) {
          const text = `Remaining Time: ${this.value}`;
          ctx.fillStyle = "#ffffff";
          ctx.font = "12px Arial";
          ctx.fillText(text, 20, y + 20);
        };
        node.addCustomWidget(widget);
        // return widget;
      },

    };
  },

});
