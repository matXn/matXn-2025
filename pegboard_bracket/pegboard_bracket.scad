// 桌面隔断横梁 洞洞板支架（纳米胶固定）
// 横梁实测：宽 45.1 mm，顶面距桌面 350 mm，可用长度约 600 mm
//
// 整个零件 = 一个 YZ 截面沿 X 拉伸 len 毫米。
// 打印时把截面平放在热床上（拉伸方向朝上），无需支撑。
//
// 坐标：X 沿横梁方向，Y 横跨横梁，Z 向上，Z=0 为横梁顶面。

/* [横梁] */
rail_w      = 45.1;  // 横梁宽度（卡尺实测）
fit_gap     = 0.3;   // 单侧装配间隙
tape_t      = 1.0;   // 纳米胶厚度（压实后）
lip_h       = 10;    // 两侧下包裙边高度（防侧滑/定位）

/* [洞洞板] */
board_t     = 5.0;   // 洞洞板厚度，按实物修改
board_gap   = 0.4;   // 插槽总间隙
board_off   = 0;     // 插槽相对横梁中心的偏移（正值偏向 +Y 一侧）

/* [支架] */
len         = 40;    // 单个支架长度（沿横梁）
wall        = 4;     // 裙边壁厚
floor_t     = 5;     // 底板厚度
slot_h      = 30;    // 插槽深度
cheek_t     = 5;     // 插槽两侧夹板厚度
chamfer     = 1.2;   // 插槽入口倒角
bolt_d      = 4.4;   // 锁紧螺栓孔（M4），0 = 不开孔

ri  = rail_w / 2 + fit_gap;           // 内腔半宽
ro  = ri + wall;                      // 外半宽
zf  = tape_t;                         // 底板下表面
zt  = tape_t + floor_t;               // 底板上表面 = 插槽底
zh  = zt + slot_h;                    // 顶部
s   = (board_t + board_gap) / 2;      // 插槽半宽
c0  = board_off - s - cheek_t;        // 夹板外侧
c1  = board_off + s + cheek_t;

module profile() {
    difference() {
        polygon([
            [-ro, -lip_h], [-ri, -lip_h], [-ri, zf], [ri, zf],
            [ ri, -lip_h], [ ro, -lip_h], [ ro, zt],
            [ c1, zh], [ c0, zh], [-ro, zt]
        ]);
        // 插槽（带入口倒角）
        polygon([
            [board_off - s, zt], [board_off + s, zt],
            [board_off + s, zh - chamfer], [board_off + s + chamfer, zh + 0.01],
            [board_off - s - chamfer, zh + 0.01], [board_off - s, zh - chamfer]
        ]);
    }
}

difference() {
    rotate([90, 0, 90]) linear_extrude(len) profile();
    if (bolt_d > 0)
        translate([len / 2, 0, zt + slot_h * 0.55])
            rotate([0, 90, 90]) cylinder(d = bolt_d, h = 4 * ro, center = true, $fn = 32);
}
