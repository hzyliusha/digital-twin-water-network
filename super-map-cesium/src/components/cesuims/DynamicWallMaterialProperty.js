// import { Color, defined, Event, Material, Property } from "cesium";
//定义材质对象及变量
 
const DynamicWallType = "DynamicWall";
 
const DynamicWallSource = /* glsl */ `czm_material czm_getMaterial(czm_materialInput materialInput)
          {
              float time = czm_frameNumber/100.0;
              czm_material material = czm_getDefaultMaterial(materialInput);
              vec2 st = materialInput.st;
              vec4 colorImage = texture2D(image, vec2(fract(1.0*st.t - time), st.t));
              material.alpha = colorImage.a * color.a;
              material.diffuse = (colorImage.rgb+color.rgb)/2.0;
              return material;
          }`; //由上到下
class DynamicWallMaterialProperty {
  constructor(image,color = Cesium.Color.WHITE, duration = 2000) {
    this._definitionChanged = new Cesium.Event();
    this._color = undefined;
    this._colorSubscription = undefined;
    this._time = new Date().getTime();
    this.image = image;
    this.color = color;
    this.duration = duration;
 
    
    //添加自定义材质
    Cesium.Material._materialCache.addMaterial(DynamicWallType, {
      fabric: {
        //纹理类型
        type: DynamicWallType,
        //传递给着色器的外部属性
        uniforms: {
          color: color.withAlpha(0.5), // 设为半透明
          image: image,
          time: -20,
        },
        //纹理资源
          source: DynamicWallSource,
        // source: _getDirectionWallShader({
        //   get: true,
        //   count: 3.0,
        //   freely: 'vertical',
        //   direction: '-'
        // })
      },
      //是否透明
      translucent: function (material) {
        return true;
      },
    });
  }
 
  get isConstant() {
    return false;
  }
 
  get definitionChanged() {
    return this._definitionChanged;
  }
 
  getType(_) {
    return DynamicWallType;
  }
 
  getValue(time, result) {
    if (!Cesium.defined(result)) {
      result = {};
    }
    result.color = Cesium.Property.getValueOrClonedDefault(
      this._color,
      time,
      Cesium.Color.WHITE,
      result.color
    );
    result.image = this.image;
    result.time =
      ((new Date().getTime() - this._time) % this.duration) / this.duration;
    return result;
  }
 
  equals(other) {
    return (
      this === other ||
      (other instanceof DynamicWallMaterialProperty &&
        Cesium.Property.equals(this._color, other._color))
    );
  }
 
}
export default DynamicWallMaterialProperty;