export default class RealLevel{
    constructor(viewer){
        this.entitiesPoint = [
            114.87868480915964, 
            29.6948214134819, 
            114.88489689766453, 
            29.689840270830658
        ]
        this.viewer = viewer
    }
    _initWarningLine(point){
        // this.viewer.scene.globe.depthTestAgainstTerrain = true;
           
        this.viewer.entities.add({
            id: 'warning',
            show: true,
            polyline: {
                positions: Cesium.Cartesian3.fromDegreesArrayHeights(point),
                width: 5,
                clampToGround: false,  // 贴面的关键
                material: Cesium.Color.RED,
                zIndex: 10000,
                // height: 30,
                // extrudedHeight: 30,
            }
        });
    }
    isShowHide(){
        let that = this;
        console.log(that.viewer.entities.getById("warning").show,"warning")
        that.viewer.entities.getById("warning").show = !that.viewer.entities.getById("warning").show
    }
    removeLine(){
        let that = this;
        console.log(that.viewer.entities.getById("warning"),"showwwwwwwwwwwwwwwww")
        let warning  = that.viewer.entities.getById("warning");
        that.viewer.entities.remove(warning)
    }
}