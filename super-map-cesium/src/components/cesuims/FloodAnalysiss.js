/**
 * @description 淹没分析函数，通过拉伸面的高度来进行分析
 */
class FloodAnalysis {
    constructor(viewer, options) {
        this.viewer = viewer;
        this.positions = options.polygon;
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
        this.waterEntity = null;
        this.waterTimer =null;
        this._init()

    }
    _init() {
        let points = this.positions
        let polygonArr = [];
        // for(let i=0;i<points.length;i++){
        //     polygonArr.push(points[i][0]);
        //     polygonArr.push(points[i][1]);
        //     polygonArr.push(0);
        // }
        points.forEach((coor) => {
            polygonArr.push(coor[0]);
            polygonArr.push(coor[1]);
            polygonArr.push(1);
        });
        this.drawWater(this.targertHeight, polygonArr, this.initialHeight);
    }
    /**
             *
             * @param {*} targetHeight 目标高度
             * @param {*} areaCoor  范围坐标
             * @param {*} waterHeight 当前水高度
             */
    drawWater(targetHeight, areaCoor, waterHeight) {
        let that = this;
        // this.viewer.entities.remove(that.waterEntity);
        this.viewer.scene.globe.depthTestAgainstTerrain = true;
        that.waterEntity = window.viewer.entities.add({
            show: this.show,
            polygon: {
                // hierarchy: new Cesium.PolygonHierarchy(
                //     Cesium.Cartesian3.fromDegreesArray(areaCoor)
                // ),
                clampToGround: true,
                hierarchy: Cesium.Cartesian3.fromDegreesArrayHeights(areaCoor),
                perPositionHeight: true,
                followSurface: true,//跟随曲面
                extrudedHeight: new Cesium.CallbackProperty(function () {  //此处用属性回调函数，直接设置extrudedHeight会导致闪烁。
                    if (waterHeight < targetHeight) {
                        waterHeight += 0.02;
                    } else {
                        waterHeight = targetHeight //给个最大值
                    }
                    // console.log(waterHeight);
                    return waterHeight
                }, false),
                material: new Cesium.Color.fromBytes(0, 102, 255, 120),
            }
        });
        
    }

    destroy() {
        this.viewer.entities.remove(this.waterEntity);
        delete this.waterEntity;
        delete this.positions;
        delete this.initialHeight;
        delete this.targertHeight;
    }
}

export default FloodAnalysis;