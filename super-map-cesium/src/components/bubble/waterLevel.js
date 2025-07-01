/**
 * @param {Viewer} viewer
 * 全局点
*/
export default class DragEntity{
    constructor(val){
        // this.viewer = val.viewer
    }
    addEntity(point,dataSource){
        let pinBuilder = new Cesium.PinBuilder();
        let poin = dataSource.entities.add({
            id:point.id,
            name: point.names,
            text: point.names,
            position : new Cesium.Cartesian3.fromDegrees(point.lng, point.lat, 75),
            type: "waterDes",
            label: { //文字标签
                text: point.names,
                font: '500 24px Microsoft YaHei',// 15pt monospace
                scale: this.scaleValue,
                style: Cesium.LabelStyle.FILL,
                fillColor: Cesium.Color.WHITE,
                color:Cesium.Color.WHITE,
                // horizontalOrigin: Cesium.HorizontalOrigin.CENTER,
                horizontalOrigin: Cesium.HorizontalOrigin.CENTER,//对齐方式
                verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
                pixelOffset: new Cesium.Cartesian2(0, -100),   //偏移量
                // eyeOffset: new Cesium.Cartesian3.fromDegrees(point.lng, point.lat, 75),
                showBackground: true,
                backgroundPadding: new Cesium.Cartesian2(10, 5),
                // disableDepthTestDistance:5000,
                disableDepthTestDistance: Number.POSITIVE_INFINITY, //去掉地形遮挡
                /**
                 * 第三个参数离地高度
                 * 和你的物体高度有关系的，比如box就是写这个box的高度的一半，中心点的高度除以二。
                    例如：15米高的物体，那么贴地就要写7.5
                */
                backgroundColor: new Cesium.Color.fromCssColorString('RGBA(61, 255, 157, 0.6)'),
                scaleByDistance: new Cesium.NearFarScalar(
                    300, 1.0, 5000, 0.7
                ),
            },
        });
        return poin
    }
    
}