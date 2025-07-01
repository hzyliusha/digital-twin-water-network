export function computeModelMatrix(entity) {
    var position = Cesium.Property.getValueOrUndefined(entity.position, Cesium.JulianDate.now());
    let modelMatrix = Cesium.Transforms.eastNorthUpToFixedFrame(position);
    return modelMatrix;
}
// 计算粒子发射器的位置姿态
export function computeEmitterModelMatrix(heading, pitch, roll) {
    let hpr = Cesium.HeadingPitchRoll.fromDegrees(heading, pitch, roll);
    let trs = new Cesium.TranslationRotationScale();
    trs.translation = Cesium.Cartesian3.fromElements(0, 0, 0);
    trs.rotation = Cesium.Quaternion.fromHeadingPitchRoll(hpr);
    let Matrix4 = Cesium.Matrix4.fromTranslationRotationScale(trs);
    return Matrix4
}
// 更新粒子运动状态
export function updateCallback(p, dt) {
    var gravityScratch = new Cesium.Cartesian3();
    var position = p.position;
    Cesium.Cartesian3.normalize(position, gravityScratch);
    Cesium.Cartesian3.fromElements(
        20 * dt,
        gravityScratch.y * dt,
        -30 * dt,
        gravityScratch
    );
    p.velocity = Cesium.Cartesian3.add(
        p.velocity,
        gravityScratch,
        p.velocity
    );
}