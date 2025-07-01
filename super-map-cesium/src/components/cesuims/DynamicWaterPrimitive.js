import {
    PrimitiveCollection,
    Primitive,
    GeometryInstance,
    PolygonHierarchy,
    EllipsoidSurfaceAppearance,
    Material,
    Cartesian3,
    ParticleSystem,
    Color,
    Cartesian2,
    CircleEmitter,
    HeadingPitchRoll,
    Transforms,
    PolygonGeometry,
    destroyObject,
  } from "cesium";
  import {nanoid} from 'nanoid'
   
//   import waterImage from "@/assets/images/material/water.png";
  import waterNormals from "@/assets/image2.png";
//   import waterGun from "@/assets/images/material/waterGun.png";
  import waterdrink from "@/assets/image2.png";
//   import DynamicHeightWaterPrimitive from "./DynamicHeightWaterPrimitive";
   
  export default class DynamicWaterPrimitive{
    constructor(args) {
      this.primitives = new PrimitiveCollection();
      this.viewer = args.viewer;
      this.viewer.scene.primitives.add(this.primitives,0);//使用前先消除，确保仅有一个
   
      this.ParticleManager = {};
   
    };
  }
   
  DynamicWaterPrimitive.getInstance = function(args) {
    if (this.instance) {
      return this.instance;
    }
    if (typeof args === 'undefined' || typeof args.viewer === 'undefined') return  null;
    return this.instance = new DynamicWaterPrimitive(args);
  }
   
  DynamicWaterPrimitive.prototype.addDynamicWater = function(options) {
    this.primitives.add(this.createDynamicWater(options))
  }
   
  DynamicWaterPrimitive.prototype.createDynamicWater = function(options) {
    let {id = nanoid(),positionArray,height } = options;
   
    return  new Primitive({
      show: true,// 默认隐藏
      allowPicking: false,
      geometryInstances: new GeometryInstance({
        id: id,
        geometry: new PolygonGeometry({
          polygonHierarchy: new PolygonHierarchy(setPositionEC(positionArray,height)),
          extrudedHeight: 0,//注释掉此属性可以只显示水面
          perPositionHeight: true//注释掉此属性水面就贴地了
        })
      }),
      // 可以设置内置的水面shader
      appearance: new EllipsoidSurfaceAppearance({
        material: new Material({
          fabric: {
            type: 'Water',
            uniforms: {
              normalMap: waterNormals,
              frequency: 1000.0,
              animationSpeed: 0.01,
              amplitude: 10.0
            }
          }
        }),
        fragmentShaderSource: 'varying vec3 v_positionMC;\n' +
          'varying vec3 v_positionEC;\n' +
          'varying vec2 v_st;\n' +
          'void main()\n' +
          '{\n' +
          'czm_materialInput materialInput;\n' +
          'vec3 normalEC = normalize(czm_normal3D * czm_geodeticSurfaceNormal(v_positionMC, vec3(0.0), vec3(1.0)));\n' +
          '#ifdef FACE_FORWARD\n' +
          'normalEC = faceforward(normalEC, vec3(0.0, 0.0, 1.0), -normalEC);\n' +
          '#endif\n' +
          'materialInput.s = v_st.s;\n' +
          'materialInput.st = v_st;\n' +
          'materialInput.str = vec3(v_st, 0.0);\n' +
          'materialInput.normalEC = normalEC;\n' +
          'materialInput.tangentToEyeMatrix = czm_eastNorthUpToEyeCoordinates(v_positionMC, materialInput.normalEC);\n' +
          'vec3 positionToEyeEC = -v_positionEC;\n' +
          'materialInput.positionToEyeEC = positionToEyeEC;\n' +
          'czm_material material = czm_getMaterial(materialInput);\n' +
          '#ifdef FLAT\n' +
          'gl_FragColor = vec4(material.diffuse + material.emission, material.alpha);\n' +
          '#else\n' +
          'gl_FragColor = czm_phong(normalize(positionToEyeEC), material, czm_lightDirectionEC);\n' +
          'gl_FragColor.a=0.85;\n' +
          '#endif\n' +
          '}\n'
      })
    });
  }
   
  function setPositionEC(positons,height, ) {
    let waterc = []
    if (isNaN(Number(height))){
      return Cartesian3.fromDegreesArray(waterc)
    }
   
    for (let index = 0; index < positons.length; index++) {
      let position = positons[index]
      waterc.push(position)
      if ((index + 1 ) % 2 === 0 && index !== 0){
        waterc.push(height)
      }
    }
    return Cartesian3.fromDegreesArrayHeights(waterc)
  }
   
   
  DynamicWaterPrimitive.prototype.createDynamicHeightWater = function(options) {
    let {positions,height = 0,extrudedHeight = 0,targetHeight = 70,growNum = 0.05,grow,materialType} = options;
   
    this.primitives.add(new DynamicHeightWaterPrimitive({
      positions : positions,
      height : height,
      extrudedHeight : extrudedHeight,
      targetHeight : targetHeight,
      grow:grow,
      materialType:materialType,
      growNum:growNum,
      loadEndCallback:(primitive) => {
        // destroyObject(primitive)
        // this.primitives.remove(primitive);
        // this.primitives.add(this.addDynamicWater({
        //   positionArray:positions,height:targetHeight
        // }))
      }
    }))
  }
   
  DynamicWaterPrimitive.prototype.createFountain = function(options) {
    let {positionArray,} = options;
   
    if (typeof positionArray !== 'undefined' && positionArray.length > 0){
      positionArray.forEach(item => {
        this.primitives.add(this.createFountainParticleSystem({
          id:nanoid(),lng: item.lng, lat:  item.lat, height: item.height,heading: item.heading,roll: item.roll
        }))
      })
    }
  }
   
  DynamicWaterPrimitive.prototype.createFountainSingle = function(options) {
    options = {id:nanoid(),...options}
    this.primitives.add(this.createFountainParticleSystem(options))
  }
   
   
  //喷泉粒子
  DynamicWaterPrimitive.prototype.createFountainParticleSystem = function (options) {
    let {lng, lat, height,heading = 0.0,pitch = 90,roll = 0.0,id} = options;
    let self = this;
    const gravityScratch = new Cartesian3();
   
    //重力参数
    function applyGravity(p, dt) {
      const position = p.position;
   
      Cartesian3.normalize(position, gravityScratch);
      Cartesian3.multiplyByScalar(
        gravityScratch,
        -8 * dt,
        gravityScratch
      );
   
      p.velocity = Cartesian3.add(
        p.velocity,
        gravityScratch,
        p.velocity
      );
    }
   
    let ps = new ParticleSystem({
      image: waterdrink,
      startColor: Color.LIGHTYELLOW.withAlpha(0.5),
      endColor: Color.LIGHTYELLOW.withAlpha(0.3),
      startScale: 2.0,
      endScale: 10.0,
      particleLife: 5.0,
      minimumSpeed: 10.0,
      maximumSpeed: 14.0,
      minimumParticleLife:1,
      maximumParticleLife:2,
      imageSize: new Cartesian2(2, 2),
      emissionRate: 30.0,
      lifetime: 12.0,
      emitter: new CircleEmitter(0.2),
      sizeInMeters: true,
      modelMatrix: Transforms.headingPitchRollToFixedFrame(Cartesian3.fromDegrees(lng, lat, height), HeadingPitchRoll.fromDegrees(heading, pitch, roll)),
      updateCallback: applyGravity,
    })
    if (!self.ParticleManager[id]){
      self.ParticleManager[id] = {
        options:options,
        particleSystem:ps,
      }
    }else if (!self.ParticleManager[id].particleSystem){
      self.ParticleManager[id].particleSystem = ps;
    }
    return ps
  }
   
   
  DynamicWaterPrimitive.prototype.clearParticle = function() {
    for(let key in this.ParticleManager){
      let manager = this.ParticleManager[key];
      this.primitives.remove(manager.particleSystem);
      this.ParticleManager[key].particleSystem = null;
    }
  }
   
  DynamicWaterPrimitive.prototype.addParticleFromCache = function() {
    for(let key in this.ParticleManager){
      let manager = this.ParticleManager[key];
      if (!manager.particleSystem){
        this.primitives.add(this.createFountainParticleSystem(manager.options))
      }
    }
  }
   
   
  DynamicWaterPrimitive.prototype.clearAll = function(options) {
    this.clearParticle()
    this.primitives.removeAll()
  }
   
  DynamicWaterPrimitive.prototype.destory = function(options) {
    this.viewer.scene.primitives.remove(this.primitives)
    this.instance = null;
  }
   