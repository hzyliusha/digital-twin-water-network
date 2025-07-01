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
        //     id:value.id,
        //     name: value.name,
        //     position: Cesium.Cartesian3.fromDegrees(value.position.x, value.position.y),
        //     billboard: {
        //       image: pinBuilder.fromText(value.text,Cesium.Color.ROYALBLUE, 48).toDataURL(),
        //       verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        //     },
        //     monitoItems:{
        //             data:value
        //         },
        id:point.id,
        name: point.name,
        text: point.name,
        position : new Cesium.Cartesian3.fromDegrees(point.lng, point.lat, 75),
        type: "area",
        label: { //文字标签
            text: point.name,
            font: '500 24px Microsoft YaHei',// 15pt monospace
            scale: this.scaleValue,
            style: Cesium.LabelStyle.FILL,
            fillColor: Cesium.Color.WHITE,
            color:Cesium.Color.WHITE,
            horizontalOrigin: Cesium.HorizontalOrigin.CENTER,
            verticalOrigin: Cesium.VerticalOrigin.TOP,
            pixelOffset: new Cesium.Cartesian2(0, -90),   //偏移量
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
            // pixelOffsetScaleByDistance: new Cesium.NearFarScalar(
            //     1.5e2, 1.0, 1.5e5, 0
            //   ),
        },
        billboard:{
            // 图像地址，URI或Canvas的属性
            image: require('@/assets/marker-area.png'),
            // 设置颜色和透明度
            // color: Cesium.Color.RED.withAlpha(0.8),
            label: { text:  point.name} ,
            // 高度（以像素为单位）
            height: 110,
            // 宽度（以像素为单位）
            width: 95,
            // 逆时针旋转
            rotation: 0,
            // 大小是否以米为单位
            sizeInMeters: false,
            // 相对于坐标的垂直位置
            verticalOrigin: Cesium.VerticalOrigin.CENTER,
            // 相对于坐标的水平位置
            horizontalOrigin: Cesium.HorizontalOrigin.CENTER,
            // 该属性指定标签在屏幕空间中距此标签原点的像素偏移量
            pixelOffset: new Cesium.Cartesian2(0, -22),
            // 应用于图像的统一比例。比例大于会1.0放大标签，而比例小于会1.0缩小标签。
            scale: this.scaleValue,
            // disableDepthTestDistance:5000,
            disableDepthTestDistance: Number.POSITIVE_INFINITY, //去掉地形遮挡
            // 是否显示
            show: true,
            scaleByDistance: new Cesium.NearFarScalar(
                300, 1.0, 5000, 0.7
            ),
            // 根据广告牌与摄像头的距离，获取或设置广告牌的近像素偏移量和远像素偏移量缩放属性  type:NearFarScalar
            // pixelOffsetScaleByDistance: new Cesium.NearFarScalar(
            //     1.5e2, 1.0, 1.5e5, 0
            // ),
         },
        monitoItems:{
            data:point
        }
        });
        return poin
    }
    
}