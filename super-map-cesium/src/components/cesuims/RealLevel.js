export default class RealLevel{
    constructor(){
        this.polygonPoint = [
            114.87964088569139, 29.693220868601853,
            114.88178224386442, 29.691510449144066,
            114.88151802514637, 29.691296767586029,
            114.87943585107534, 29.692955184121556,
        ]
    }
    async _initWater(dataSource, waterNum){
        let style = {
            text: `实时水位: ${waterNum} m`,
            fontSize: 24,
            color: "#fff",
        }
        console.log(style.text, 'textsssssssss');
        
        let polyData = dataSource.entities.add({
            show: true,
            polygon: {
                hierarchy: Cesium.Cartesian3.fromDegreesArray(this.polygonPoint),
                material: new Cesium.ImageMaterialProperty({
                    image: this.createdText(style),
                    transparent: true,
                    color: Cesium.Color.WHITE
                }),
                // perPositionHeight: true,
                maximumHeights:[100,100],
                zIndex: 10000,
                height: 1,
                // extrudedHeight: 120,
                rotation: Cesium.Math.toRadians(223),//指定椭圆从北方逆时针旋转 40
                stRotation: Cesium.Math.toRadians(223), //指定椭圆纹理从北方逆时针旋转 40
                classificationType: Cesium.ClassificationType.BOTH,
                outline : true,
                outlineColor : Cesium.Color.BLACK
            },
        })
        return polyData
    }
    createdText(obj){
        const text = obj.text;
        var textCanvas = document.createElement("canvas");
        const width = text.length * obj.fontSize;
        textCanvas.width = width;
        textCanvas.height = 40;
        var ctx = textCanvas.getContext("2d");
        ctx.fillStyle = obj.color;
        ctx.font = " " + obj.fontSize + "px 微软雅黑"; //设置字体
        ctx.textBaseline = 'hanging'; //在绘制文本时使用的当前文本基线 
        //绘制文本  
        ctx.fillText(text, 5, 5);
        return textCanvas.toDataURL('image/png')
    }
}