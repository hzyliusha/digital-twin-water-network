/**
 * @description 淹没分析函数，通过拉伸面的高度来进行分析
 */
//  import Vue from "vue";
//  import TimeLine from "./FloodAnalysisTimeLIne.vue";
//  let WindowVm = Vue.extend(TimeLine);
 class FloodAnalysis {
    constructor(viewer, options) {
      this.positions = this.CoorsFormt(options.polygon);
      this.times_height = options.times_height;
      this.currentIndex = 0;
      this.initialHeight = this.times_height[this.currentIndex];
      this.targertHeight = this.times_height[this.currentIndex + 1];
      this.increaseHeight = this.targertHeight - this.initialHeight;
      this.waterColor = options.waterColor;
      this.show = options.show;
      this.start = null;
      this.clockEven = null
      this.pageData = options.pageData
     
      //以下代码为自定义时间轴样式，未完成，暂停
      // this.vmInstance = new WindowVm({
      //   propsData: {
      //    timeData,
      //    heightRange:this.times_height,
      //   }
      // }).$mount(); //根据模板创建一个面板
      // this.vmInstance.startOrendClick = e => {
      //   window.viewer.clock.canAnimate = e;//时间轴暂停/开启
      //   window.viewer.clock.shouldAnimate = e;//暂停、开启
      // }
      this.init();
      this.getNowHeight();
    }
    CoorsFormt(coors) {
      let Arr = [];
      coors.forEach((coor) => {
        Arr.push(coor[0]);
        Arr.push(coor[1]);
      });
      return Arr;
    }
    async init() {
      this.viewerSET();
      const self = this;
      this.property = this.computeFlight();
      window.viewer.scene.globe.depthTestAgainstTerrain = true;
    
      this.entity = window.viewer.entities.add({
        show: this.show,
        ////与时间轴关联
        availability: new Cesium.TimeIntervalCollection([
          new Cesium.TimeInterval({
            start: this.start,
            stop:Cesium.JulianDate.fromDate(self.pageData.endTime)
            // stop: Cesium.JulianDate.addMinutes(
            //   this.start,
            //   1 * this.times_height.length,
            //   new Cesium.JulianDate()
            // ),
          }),
        ]),
        polygon: {
          hierarchy: new Cesium.PolygonHierarchy(
            Cesium.Cartesian3.fromDegreesArray(this.positions)
          ),
          extrudedHeight: this.property,//是指polygon拉伸后距离地面的拉伸高度  只有当extrudedHeight大雨height时才会出现挤出高度的效果，且polygon的厚度是两者的差值
          height:this.property,// 是指polygon距离地面的高度
          material: Cesium.Color.fromCssColorString(this.waterColor)
        },
      });
        
        
    }
  /*
  *时间水位与时间关联 
  */
    computeFlight() {
      let data = this.pageData.dataList
      let property = new Cesium.SampledProperty(Number);
      data.forEach((item, i) => {
        property.addSample(
          Cesium.JulianDate.addHours(
            this.start,
            1 * i,
            new Cesium.JulianDate()
          ),
          item.sw
        );
        //最后一个小时没数据
        if(i == data.length - 1){
          property.addSample(
            Cesium.JulianDate.addHours(
              this.start,
              1* (i + 1),
              new Cesium.JulianDate()
            ),
            item.sw
          );
        }
        
        // property.addSample(
        //   Cesium.JulianDate.addMinutes(
        //     this.start,
        //     1 * i,
        //     new Cesium.JulianDate()
        //   ),
        //   item
        // );
      });
      console.log('computeFlight')

      /*******下面代码是自定义时间回调函数返回水面高度，目前作废 */
      // let self = this
      // let property = new Cesium.CallbackProperty(function(time,result){
      //   //计算当前时间的实时位置
      //   let diff = Cesium.JulianDate.secondsDifference(time, self.start)
      //   // console.log(diff)
      //   let currentHeight = self.initialHeight + self.increaseHeight / 120 * diff;
      //   let timeIndex = parseInt(currentHeight)
      //   if (diff == 120) {
      //     currentHeight = self.targertHeight
      //   }
      //   // console.log(self.vmInstance)
      //   self.vmInstance.setTimeIndex(currentHeight)
      //   return currentHeight
      // })

      return property;
    }
  /*
  *设置时间
  */
    viewerSET() {
      console.log('viewerSET')
    //   document.getElementsByClassName('cesium-viewer-animationContainer')[0].setAttribute('style','display: normal;')
    //   document.getElementsByClassName('cesium-viewer-timelineContainer')[0].setAttribute('style','display: normal;')
      let startTime = this.pageData.startTime
      let endTime = this.pageData.endTime
      this.start = Cesium.JulianDate.fromDate(startTime);
      console.log(this.start,"this.start")
      this.stop = Cesium.JulianDate.fromDate(endTime);
      window.viewer.clock.startTime = this.start.clone();
      window.viewer.clock.currentTime = this.start.clone();
      window.viewer.clock.stopTime = this.stop.clone();
      window.viewer.clock.canAnimate = true;//时间轴开启
      window.viewer.clock.shouldAnimate = true;//开启
      window.viewer.clock.multiplier = 3600 // 时间速率，数字越大时间过的越快
      if (window.viewer.timeline)
      window.viewer.timeline.zoomTo(this.start, this.stop);
      //clockRange属性表示时间轴达到终点之后的行为，用户可以根据自己的需要来设置，默认为: UNBOUNDED
      // CLAMPED：达到终止时间后停止
      // LOOP_STOP：达到终止时间后重新循环
      // UNBOUNDED：达到终止时间后继续读秒
      window.viewer.clock.clockRange = Cesium.ClockRange.CLAMPED;
    }
    /**
     * 获取实时水面高度
     * 时钟滴答，一直在走
     */
    getNowHeight() {
      const self = this;
      self.clockEven = window.viewer.clock.onTick.addEventListener(function () {
        if (self.increaseHeight > 0) {
          if (self.initialHeight > self.targertHeight) {
            self.currentIndex += 1;
            if (self.currentIndex > self.times_height.length - 2) {
              self.currentIndex = 0;
            }
            self.initialHeight = self.times_height[self.currentIndex];
            self.targertHeight = self.times_height[self.currentIndex + 1];
            self.increaseHeight = self.targertHeight - self.initialHeight;
          }
        }
        if (self.increaseHeight < 0) {
          if (self.initialHeight < self.targertHeight) {
            self.currentIndex += 1;
            if (self.currentIndex > self.times_height.length - 2) {
              self.currentIndex = 0;
            }
            self.initialHeight = self.times_height[self.currentIndex];
            self.targertHeight = self.times_height[self.currentIndex + 1];
            self.increaseHeight = self.targertHeight - self.initialHeight;
          }
        }
        self.initialHeight += self.increaseHeight / 10;
        // console.log("self.initialHeight:"+self.initialHeight)
      });
    }
   
    /**
     * 改变颜色
     * @param {水体颜色} val
     */
    changeWaterColor(val) {
      this.entity.polygon.material = val;
    }
    /**
     * 隐藏与显示
     * @param {Boolean} val
     */
    changeWaterShow(val) {
      this.entity.show = val;
    }
   
    destroy() {
    //   document.getElementsByClassName('cesium-viewer-animationContainer')[0].setAttribute('style','display: none;')
    //   document.getElementsByClassName('cesium-viewer-timelineContainer')[0].setAttribute('style','display: none;')
      window.viewer.clock.canAnimate = false;//时间轴暂停
      window.viewer.clock.shouldAnimate = false;//暂停
      // 重置
      window.viewer.clock.currentTime = this.start.clone();
      this.clockEven()
      window.viewer.entities.remove(this.entity);
      
      delete this.entity;
      delete this.positions;
      delete this.initialHeight;
      delete this.targertHeight;
      delete this.increaseHeight;
      delete this.pageData
      delete this.clockEven

      
      // if(this.vmInstance){
      //   this.vmInstance.$el.remove();
      //   this.vmInstance.$destroy();
      // }
    }
  }
   
  export default FloodAnalysis;