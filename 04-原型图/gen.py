#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""053 题库系统 UI 原型生成器：统一壳体 + 页面内容块，输出可点击可跳转的 HTML mock"""
import pathlib

OUT = pathlib.Path(__file__).parent
C = dict(primary="#4B3F72", sub="#7A6BA8", accent="#E0A458", bg="#F5F6F7",
         text="#1F2933", muted="#5B6770", ok="#2B7955", danger="#B02A37")

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:"PingFang SC","Microsoft YaHei",system-ui,sans-serif;background:%(bg)s;color:%(text)s;font-size:13px}
a{color:inherit;text-decoration:none}
.num{font-variant-numeric:tabular-nums;font-feature-settings:"tnum"}
.sidebar{position:fixed;left:0;top:0;bottom:0;width:220px;background:%(primary)s;color:#fff;display:flex;flex-direction:column}
.logo{height:56px;display:flex;align-items:center;gap:9px;padding:0 18px;font-size:15px;font-weight:600;letter-spacing:.5px;border-bottom:1px solid rgba(255,255,255,.12)}
.logo i{width:22px;height:22px;border-radius:6px;background:%(accent)s;display:inline-block}
.nav{flex:1;overflow:auto;padding:8px 0}
.nav .g{padding:12px 18px 6px;font-size:11px;color:rgba(255,255,255,.45);letter-spacing:1px}
.nav a{display:flex;align-items:center;gap:9px;padding:9px 18px;font-size:13px;color:rgba(255,255,255,.82);border-left:3px solid transparent}
.nav a:hover{background:rgba(255,255,255,.08);color:#fff}
.nav a.on{background:rgba(255,255,255,.14);color:#fff;border-left-color:%(accent)s;font-weight:600}
.nav a .dot{width:5px;height:5px;border-radius:50%%;background:rgba(255,255,255,.4)}
.nav a.on .dot{background:%(accent)s}
.main{margin-left:220px;min-height:100vh}
.top{height:56px;background:#fff;border-bottom:1px solid #E4E7EB;display:flex;align-items:center;padding:0 24px;gap:14px;position:sticky;top:0;z-index:9}
.crumb{font-size:12px;color:%(muted)s}.crumb b{color:%(text)s;font-weight:600}
.top .sp{margin-left:auto}
.icon-btn{width:32px;height:32px;border-radius:8px;display:flex;align-items:center;justify-content:center;color:%(muted)s;cursor:pointer}
.icon-btn:hover{background:#F1F2F4}
.ava{width:30px;height:30px;border-radius:50%%;background:%(sub)s;color:#fff;display:flex;align-items:center;justify-content:center;font-size:11px}
.who{font-size:12px;line-height:1.3}.who span{color:%(muted)s;font-size:11px}
.body{padding:24px}
.card{background:#fff;border:1px solid #E4E7EB;border-radius:10px;margin-bottom:16px;overflow:hidden}
.card-h{display:flex;align-items:center;gap:10px;padding:14px 16px;border-bottom:1px solid #EEF0F2}
.card-h h2{font-size:14px;font-weight:600}.card-h .sub{font-size:12px;color:%(muted)s}
.card-b{padding:16px}
.grid{display:grid;gap:14px}
.kpi{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.kpi .k{background:#fff;border:1px solid #E4E7EB;border-radius:10px;padding:14px 16px}
.kpi .k .t{font-size:12px;color:%(muted)s;display:flex;align-items:center;gap:6px}
.kpi .k .v{font-size:26px;font-weight:700;letter-spacing:-.5px;margin-top:6px;color:%(primary)s}
.kpi .k .d{font-size:11px;color:%(muted)s;margin-top:2px}
.btn{height:32px;padding:0 14px;border-radius:7px;border:1px solid #D6DAE0;background:#fff;color:%(text)s;font-size:13px;cursor:pointer;display:inline-flex;align-items:center;gap:6px}
.btn:hover{border-color:%(sub)s;color:%(primary)s}
.btn.p{background:%(primary)s;border-color:%(primary)s;color:#fff}.btn.p:hover{background:#3C3260;color:#fff}
.btn.a{background:%(accent)s;border-color:%(accent)s;color:#3A2A10}
.btn.d{border-color:%(danger)s;color:%(danger)s;background:#fff}
.btn.sm{height:26px;padding:0 9px;font-size:12px;border-radius:6px}
.inp{height:32px;border:1px solid #D6DAE0;border-radius:7px;padding:0 10px;font-size:13px;color:%(text)s;background:#fff;min-width:180px}
.inp.wide{min-width:360px}
.filter{display:flex;flex-wrap:wrap;gap:10px;align-items:center}
.filter label{font-size:12px;color:%(muted)s}
table{width:100%%;border-collapse:collapse}
th{text-align:left;font-size:12px;font-weight:600;color:%(muted)s;background:#FAFBFC;padding:10px 12px;border-bottom:1px solid #E4E7EB;white-space:nowrap}
td{padding:11px 12px;border-bottom:1px solid #EEF0F2;font-size:13px;vertical-align:middle}
tbody tr:hover{background:#FBFAFD}
.tag{display:inline-flex;align-items:center;gap:4px;height:22px;padding:0 8px;border-radius:5px;font-size:11px;font-weight:600;border:1px solid}
.tag.ok{color:%(ok)s;background:#EAF4EF;border-color:#C6E0D3}
.tag.warn{color:#8A5A12;background:#FDF3E3;border-color:#F0D9B0}
.tag.err{color:%(danger)s;background:#FBEBED;border-color:#EFC9CE}
.tag.info{color:%(sub)s;background:#F0EEF7;border-color:#D9D3EC}
.tag.gray{color:%(muted)s;background:#F2F4F6;border-color:#E1E5E9}
.pager{display:flex;justify-content:flex-end;align-items:center;gap:6px;padding:14px 16px;font-size:12px;color:%(muted)s}
.pager b{min-width:28px;height:28px;border:1px solid #D6DAE0;border-radius:6px;display:inline-flex;align-items:center;justify-content:center;color:%(text)s;font-weight:400}
.pager b.on{background:%(primary)s;border-color:%(primary)s;color:#fff}
.bar{height:8px;border-radius:4px;background:#EDEFF2;overflow:hidden}
.bar i{display:block;height:100%%;border-radius:4px;background:%(primary)s}
.bar i.a{background:%(accent)s}.bar i.ok{background:%(ok)s}.bar i.d{background:%(danger)s}
.muted{color:%(muted)s;font-size:12px}
.h3{font-size:13px;font-weight:600;margin-bottom:10px;display:flex;align-items:center;gap:7px}
.h3:before{content:"";width:3px;height:13px;border-radius:2px;background:%(primary)s;display:inline-block}
.form-row{display:flex;margin-bottom:14px;align-items:flex-start}
.form-row>label{width:110px;flex:none;text-align:right;padding-right:14px;font-size:13px;color:%(muted)s;line-height:32px}
.form-row .ctl{flex:1}
.two{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.three{display:grid;grid-template-columns:1fr 360px;gap:16px}
.chart{height:220px;background:linear-gradient(180deg,#FCFCFD,#F7F8FA);border:1px dashed #DFE3E8;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#98A2B3;font-size:12px}
/* 门户壳体（学生端） */
.portal-top{height:60px;background:%(primary)s;color:#fff;display:flex;align-items:center;padding:0 40px;gap:26px}
.portal-top .brand{font-size:16px;font-weight:600;display:flex;align-items:center;gap:9px}
.portal-top .brand i{width:22px;height:22px;border-radius:6px;background:%(accent)s;display:inline-block}
.portal-top nav{display:flex;gap:4px}
.portal-top nav a{padding:7px 14px;border-radius:7px;font-size:13px;color:rgba(255,255,255,.8)}
.portal-top nav a.on{background:rgba(255,255,255,.16);color:#fff;font-weight:600}
.portal-wrap{max-width:1240px;margin:0 auto;padding:24px}
.opt{display:flex;align-items:center;gap:10px;border:1px solid #D6DAE0;border-radius:8px;padding:11px 14px;margin-bottom:10px;background:#fff}
.opt.sel{border-color:%(primary)s;background:#F7F5FC}
.opt .lb{width:22px;height:22px;border-radius:50%%;border:1px solid #C9CED6;display:flex;align-items:center;justify-content:center;font-size:11px;color:%(muted)s;flex:none}
.opt.sel .lb{background:%(primary)s;border-color:%(primary)s;color:#fff}
.steps{display:flex;gap:0;margin-bottom:18px}
.steps .s{flex:1;display:flex;align-items:center;gap:8px;font-size:12px;color:%(muted)s}
.steps .s .n{width:22px;height:22px;border-radius:50%%;border:1px solid #D6DAE0;display:flex;align-items:center;justify-content:center;font-size:11px}
.steps .s.on{color:%(primary)s;font-weight:600}.steps .s.on .n{background:%(primary)s;border-color:%(primary)s;color:#fff}
.steps .s:after{content:"";flex:1;height:1px;background:#E4E7EB;margin:0 10px}
.steps .s:last-child:after{display:none}
.drawer{position:fixed;right:0;top:0;bottom:0;width:420px;background:#fff;box-shadow:-8px 0 30px rgba(20,20,40,.12);padding:20px}
"""


def shell(title, crumb, nav_html, body, active=""):
    return f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<title>{title} · 智汇题库</title><style>{CSS % C}</style></head><body>
<div class="sidebar"><div class="logo"><i></i>智汇题库</div><div class="nav">{nav_html}</div>
<div style="padding:14px 18px;border-top:1px solid rgba(255,255,255,.12);font-size:11px;color:rgba(255,255,255,.5)">2026 春季学期 · 教研版</div></div>
<div class="main"><div class="top"><div class="crumb">首页 / <b>{crumb}</b></div>
<div class="sp"></div><div class="icon-btn">🔔</div><div class="icon-btn">?</div>
<div class="ava">李</div><div class="who">李静<br><span>教研员 · 数学教研室</span></div></div>
<div class="body">{body}</div></div></body></html>"""


ADMIN_NAV = """
<div class="g">题库中心</div>
<a href="dashboard.html"><span class="dot"></span>题库统计首页</a>
<a href="subject.html"><span class="dot"></span>学科管理</a>
<a href="knowledge-tree.html"><span class="dot"></span>知识点树</a>
<a href="question-list.html"><span class="dot"></span>题库列表</a>
<a href="question-edit.html"><span class="dot"></span>题目编辑</a>
<div class="g">组卷与练习</div>
<a href="paper-workbench.html"><span class="dot"></span>组卷工作台</a>
<a href="paper-list.html"><span class="dot"></span>试卷管理</a>
<a href="audit.html"><span class="dot"></span>题目审核台</a>
<a href="import.html"><span class="dot"></span>批量导入</a>
<div class="g">学情诊断</div>
<a href="mastery.html"><span class="dot"></span>学情诊断</a>
<a href="class-stat.html"><span class="dot"></span>班级学情</a>
<a href="rule-config.html"><span class="dot"></span>诊断规则配置</a>
<div class="g">系统管理</div>
<a href="user-role.html"><span class="dot"></span>用户与角色</a>"""


def mark(nav):
    """把当前页的导航项加 on：调用方传文件名"""
    def f(active):
        out = nav.replace(f'<a href="{active}.html">', f'<a class="on" href="{active}.html">')
        return out
    return f


def portal(title, active, body):
    navs = [("practice-center", "练习中心"), ("wrong-book", "我的错题本"),
            ("mastery-student", "我的学情诊断"), ("paper-list", "试卷库")]
    nav = "".join(f'<a class="{"on" if k == active else ""}" href="{k}.html">{v}</a>' for k, v in navs)
    return f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><title>{title} · 智汇题库</title>
<style>{CSS % C}</style></head><body>
<div class="portal-top"><div class="brand"><i></i>智汇题库 · 学生端</div><nav>{nav}</nav>
<div style="margin-left:auto;display:flex;align-items:center;gap:10px;font-size:12px">陈皓 · 计算机 2301<div class="ava">陈</div></div></div>
<div class="portal-wrap">{body}</div></body></html>"""


pages = {}

# ---------- 1 登录 ----------
pages["login"] = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><title>登录 · 智汇题库</title>
<style>{CSS % C}
body{{height:100vh;overflow:hidden;background:#fff}}
.split{{display:flex;height:100vh}}
.left{{width:52%;background:{C['primary']};color:#fff;padding:56px 64px;position:relative;overflow:hidden}}
.left:before{{content:"";position:absolute;right:-120px;top:-120px;width:420px;height:420px;border-radius:50%;background:rgba(122,107,168,.55)}}
.left:after{{content:"";position:absolute;left:-80px;bottom:-140px;width:340px;height:340px;border-radius:50%;background:rgba(224,164,88,.22)}}
.left .brand{{display:flex;align-items:center;gap:10px;font-size:17px;font-weight:600}}
.left .brand i{{width:26px;height:26px;border-radius:7px;background:{C['accent']};display:inline-block}}
.left h1{{font-size:40px;line-height:1.35;margin-top:64px;font-weight:700;letter-spacing:-.5px;position:relative;z-index:2}}
.left p{{margin-top:18px;font-size:14px;line-height:2;color:rgba(255,255,255,.72);position:relative;z-index:2;max-width:420px}}
.left .pts{{margin-top:44px;display:grid;gap:14px;position:relative;z-index:2}}
.left .pts div{{display:flex;gap:10px;align-items:center;font-size:13px;color:rgba(255,255,255,.86)}}
.left .pts b{{width:24px;height:24px;border-radius:7px;background:rgba(255,255,255,.16);display:flex;align-items:center;justify-content:center;font-size:12px}}
.right{{flex:1;display:flex;align-items:center;justify-content:center}}
.form{{width:380px}}
.form h2{{font-size:24px;font-weight:700}}
.form .sub{{margin:8px 0 30px;color:{C['muted']};font-size:13px}}
.field{{margin-bottom:16px}}
.field label{{display:block;font-size:12px;color:{C['muted']};margin-bottom:7px}}
.field .box{{height:44px;border:1px solid #D6DAE0;border-radius:9px;display:flex;align-items:center;padding:0 13px;gap:9px;font-size:13px;color:#98A2B3}}
.field .box.on{{border-color:{C['primary']};box-shadow:0 0 0 3px rgba(75,63,114,.1)}}
.row{{display:flex;justify-content:space-between;font-size:12px;color:{C['muted']};margin:4px 0 22px}}
.submit{{width:100%;height:44px;border-radius:9px;background:{C['primary']};color:#fff;border:0;font-size:14px;font-weight:600;cursor:pointer}}
.roles{{margin-top:26px;padding-top:18px;border-top:1px solid #EEF0F2;font-size:12px;color:{C['muted']}}}
.roles .r{{display:flex;gap:8px;margin-top:9px;flex-wrap:wrap}}
.roles .r span{{padding:4px 10px;border:1px solid #E4E7EB;border-radius:20px;font-size:11px}}
</style></head><body><div class="split">
<div class="left"><div class="brand"><i></i>智汇题库</div>
<h1>让每道错题<br>都变成一次诊断</h1>
<p>按知识点组卷、在线练习自动判分，交卷即生成错题本；五项因子加权输出掌握度，教师与学生看到同一套口径。</p>
<div class="pts"><div><b>1</b>三级知识点树 · 考纲权重组卷</div><div><b>2</b>交卷秒判 · 错题自动归档</div><div><b>3</b>掌握度诊断 · 结果可追溯可修正</div></div></div>
<div class="right"><div class="form"><h2>欢迎回来</h2><div class="sub">请使用学校统一账号登录</div>
<div class="field"><label>账号</label><div class="box on">👤 2023010101</div></div>
<div class="field"><label>密码</label><div class="box">🔒 ··········</div></div>
<div class="row"><span>☐ 记住我</span><span>忘记密码？联系教研秘书</span></div>
<a href="dashboard.html"><button class="submit">登 录</button></a>
<div class="roles">演示账号（密码 123456）<div class="r"><span>admin 管理员</span><span>teacher01 任课教师</span><span>auditor 教研员</span><span>secretary 教学秘书</span><span>2023010101 学生</span></div></div>
</div></div></div></body></html>"""

# ---------- 2 题库统计首页 ----------
kpis = [("题目总数", "2,486", "较上月 +128"), ("待审核题目", "37", "其中超时 4 条"),
        ("本月新增", "128", "覆盖 6 个学科"), ("练习人次", "1,942", "近 30 天"),
        ("平均正确率", "72.4%", "同比 +3.1pt"), ("错题总量", "3,105", "待复习 812"),
        ("薄弱知识点", "14", "掌握度低于 50"), ("活跃学生", "486", "近 7 天登录")]
kpi_html = "".join(f'<div class="k"><div class="t">{t}</div><div class="v num">{v}</div><div class="d">{d}</div></div>' for t, v, d in kpis)
subj = [("高等数学", 742, 68), ("数据结构", 618, 61), ("大学物理", 436, 54), ("线性代数", 402, 47), ("程序设计基础", 288, 56)]
ring = "".join(f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:11px"><span style="width:88px;font-size:12px">{n}</span>'
               f'<div class="bar" style="flex:1"><i style="width:{p}%"></i></div><b class="num" style="font-size:12px">{q}</b></div>'
               for n, q, p in subj)
pages["dashboard"] = shell("题库统计首页", "题库统计首页", mark(ADMIN_NAV)("dashboard"), f"""
<div class="filter" style="margin-bottom:16px">
  <select class="inp"><option>最近 30 天</option><option>本学期</option><option>自定义区间</option></select>
  <select class="inp"><option>全部学科</option><option>高等数学</option><option>数据结构</option></select>
  <select class="inp"><option>全部层次</option><option>本科</option><option>高职</option></select>
  <button class="btn p">查询</button><button class="btn">导出报表</button>
  <span class="muted" style="margin-left:auto">口径：统计区间内已交卷练习，作废记录不计入</span>
</div>
<div class="kpi" style="grid-template-columns:repeat(4,1fr);margin-bottom:16px">{kpi_html}</div>
<div class="grid" style="grid-template-columns:1.35fr 1fr;margin-bottom:16px">
  <div class="card" style="margin:0"><div class="card-h"><h2>近 30 天练习量与正确率</h2><span class="sub">双轴折线</span></div>
    <div class="card-b"><div class="chart" style="height:196px">练习量（柱）+ 正确率（线）双轴图</div></div></div>
  <div class="card" style="margin:0"><div class="card-h"><h2>学科题量占比</h2><span class="sub">环形图</span></div>
    <div class="card-b">{ring}</div></div>
</div>
<div class="grid" style="grid-template-columns:1fr 1fr 1fr">
  <div class="card" style="margin:0"><div class="card-h"><h2>题目难度分布</h2></div><div class="card-b"><div class="chart" style="height:150px">难度 0.1-1.0 分档柱状图</div></div></div>
  <div class="card" style="margin:0"><div class="card-h"><h2>错题重练转化</h2></div><div class="card-b"><div class="chart" style="height:150px">未掌握 → 复习中 → 已掌握 漏斗</div></div></div>
  <div class="card" style="margin:0"><div class="card-h"><h2>薄弱知识点 Top5</h2></div><div class="card-b">
    {''.join(f'<div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px dashed #EEF0F2;font-size:12px"><span>{n}</span><span class="tag err">掌握度 {v}</span></div>' for n, v in [("定积分换元法",42),("二叉树遍历",47),("电磁感应",49),("特征值与特征向量",51),("指针与引用",53)])}
  </div></div>
</div>""")

# ---------- 3 学科管理 ----------
rows = [("XK001", "高等数学", "本科", "数学教研室", "李静", 742, "60.00", "启用"),
        ("XK002", "数据结构", "本科", "计算机学院", "王振", 618, "60.00", "启用"),
        ("XK003", "大学物理", "本科", "物理教研室", "周敏", 436, "60.00", "启用"),
        ("XK004", "线性代数", "本科", "数学教研室", "李静", 402, "60.00", "启用"),
        ("XK005", "程序设计基础", "本科", "计算机学院", "王振", 288, "60.00", "启用"),
        ("XK006", "离散数学", "本科", "计算机学院", "赵磊", 0, "60.00", "停用")]
tr = "".join(f"""<tr><td class="num">{a}</td><td><b>{b}</b></td><td>{c}</td><td>{d}</td><td>{e}</td>
<td class="num">{f}</td><td class="num">{g}</td><td><span class="tag {'ok' if h == '启用' else 'gray'}">{h}</span></td>
<td><button class="btn sm">编辑</button> <button class="btn sm d">删除</button></td></tr>""" for a, b, c, d, e, f, g, h in rows)
pages["subject"] = shell("学科管理", "学科管理", mark(ADMIN_NAV)("subject"), f"""
<div class="card"><div class="card-b"><div class="filter">
<input class="inp" placeholder="学科编号 / 名称"><select class="inp"><option>全部层次</option><option>本科</option><option>高职</option></select>
<select class="inp"><option>全部状态</option><option>启用</option><option>停用</option></select>
<button class="btn p">查询</button><button class="btn">重置</button>
<button class="btn p" style="margin-left:auto">+ 新建学科</button></div></div></div>
<div class="card"><div class="card-h"><h2>学科列表</h2><span class="sub">共 6 条</span></div>
<table><thead><tr><th>学科编号</th><th>学科名称</th><th>适用层次</th><th>开课院系</th><th>负责人</th><th>题目总数</th><th>默认及格率</th><th>状态</th><th>操作</th></tr></thead>
<tbody>{tr}</tbody></table>
<div class="pager"><span>共 6 条</span><b class="on">1</b><b>2</b><b>›</b><select class="inp" style="min-width:90px;height:28px"><option>10 条/页</option></select></div></div>""")

# ---------- 4 知识点树 ----------
def kp(name, w, q, lv=1, open_=False, children=""):
    pad = (lv - 1) * 22
    return f"""<div style="padding:8px 10px;border-radius:7px;display:flex;align-items:center;gap:8px;{'background:#F7F5FC' if open_ else ''}">
<div style="padding-left:{pad}px;display:flex;align-items:center;gap:8px;flex:1">
<span style="color:#98A2B3;font-size:11px">{'▾' if open_ else '▸'}</span><span style="font-size:{13 - (lv-1)}px;font-weight:{600 if lv == 1 else 400}">{name}</span>
<span class="tag gray">L{lv}</span></div>
<span class="muted num" style="width:64px;text-align:right">权重 {w}</span>
<span class="muted num" style="width:64px;text-align:right">题量 {q}</span>
<button class="btn sm">编辑</button></div>{children}"""

tree = (kp("函数与极限", "22.00", 168, 1, True,
           kp("数列极限", "8.00", 62, 2) + kp("函数连续性", "6.00", 44, 2) +
           kp("无穷小比较", "4.00", 38, 2) + kp("两个重要极限", "4.00", 24, 2)) +
        kp("一元函数微分学", "26.00", 214, 1, True,
           kp("导数定义与计算", "10.00", 96, 2) + kp("微分中值定理", "8.00", 72, 2) + kp("导数应用", "8.00", 46, 2)) +
        kp("一元函数积分学", "30.00", 236, 1, True,
           kp("不定积分", "10.00", 88, 2,
              kp("换元积分法", "4.00", 42, 3) + kp("分部积分法", "3.00", 28, 3) + kp("有理函数积分", "3.00", 18, 3)) +
           kp("定积分", "12.00", 94, 2) + kp("定积分应用", "8.00", 54, 2)) +
        kp("多元函数微积分", "16.00", 124, 1, True,
           kp("偏导数与全微分", "9.00", 78, 2) + kp("二重积分", "7.00", 46, 2)) +
        kp("常微分方程", "6.00", 0, 1, False))
pages["knowledge-tree"] = shell("知识点树", "知识点树", mark(ADMIN_NAV)("knowledge-tree"), f"""
<div class="filter" style="margin-bottom:16px">
<select class="inp"><option>高等数学</option><option>数据结构</option></select>
<input class="inp" placeholder="知识点名称"><button class="btn p">查询</button>
<span class="muted" style="margin-left:auto">一级节点权重合计 <b style="color:{C['primary']}">100.00</b> / 上限 100</span>
<button class="btn">批量调整权重</button><button class="btn p">+ 新增知识点</button></div>
<div class="three">
<div class="card" style="margin:0"><div class="card-h"><h2>知识点树</h2><span class="sub">支持拖拽调整父级，跨学科拖动将被拒绝</span></div>
<div class="card-b" style="padding:10px">{tree}</div></div>
<div class="card" style="margin:0;align-self:start"><div class="card-h"><h2>节点详情</h2></div><div class="card-b">
<div class="form-row"><label>知识点编号</label><div class="ctl"><span class="num">ZS01-0012</span></div></div>
<div class="form-row"><label>知识点名称</label><div class="ctl"><input class="inp wide" value="换元积分法"></div></div>
<div class="form-row"><label>所属学科</label><div class="ctl">高等数学</div></div>
<div class="form-row"><label>上级知识点</label><div class="ctl">不定积分（L2）</div></div>
<div class="form-row"><label>层级</label><div class="ctl"><span class="tag info">第三级</span></div></div>
<div class="form-row"><label>考纲权重</label><div class="ctl"><input class="inp" value="4.00" style="width:120px"> <span class="muted">%</span></div></div>
<div class="form-row"><label>掌握阈值</label><div class="ctl"><input class="inp" value="80.00" style="width:120px"> <span class="muted">%</span></div></div>
<div class="form-row"><label>关联题量</label><div class="ctl"><b class="num">42</b> 道（已入库 38 / 待审核 4）</div></div>
<div class="form-row"><label>状态</label><div class="ctl"><span class="tag ok">启用</span></div></div>
<div style="display:flex;gap:8px;margin-left:110px"><button class="btn p">保存</button><button class="btn">停用</button></div>
<div class="muted" style="margin:16px 0 0 110px;line-height:1.7">停用后组卷可选中但不参与抽题；删除前将校验题目与错题引用。</div>
</div></div></div>""")

# ---------- 5 题库列表 ----------
qs = [("TM01000001", "高等数学", "换元积分法", "单选", "设函数 f(x)=x²+2x，则 f'(1) 的值为（ ）", 0.45, 5.0, "已入库", 62.4),
      ("TM01000002", "高等数学", "分部积分法", "多选", "下列积分中可以使用分部积分法求解的有（ ）", 0.62, 5.0, "已入库", 51.8),
      ("TM01000003", "高等数学", "定积分", "判断", "定积分的值一定大于零。", 0.30, 2.0, "已入库", 88.2),
      ("TM01000004", "高等数学", "两个重要极限", "填空", "lim(x→0) sin x / x = ____", 0.35, 4.0, "待审核", 0.0),
      ("TM01000005", "数据结构", "二叉树遍历", "单选", "对二叉树进行中序遍历，得到的序列（ ）", 0.55, 5.0, "已入库", 47.6),
      ("TM01000006", "数据结构", "指针与引用", "简答", "简述 C 语言中指针与引用的区别，并各举一例。", 0.68, 10.0, "已入库", 58.3),
      ("TM01000007", "高等数学", "偏导数与全微分", "计算", "求 z = x²y + sin(xy) 的全微分 dz。", 0.72, 12.0, "草稿", 0.0),
      ("TM01000008", "高等数学", "导数应用", "单选", "函数单调递增区间为（ ）", 0.48, 5.0, "已驳回", 0.0)]
def qtag(s):
    return {"已入库": "ok", "待审核": "warn", "草稿": "gray", "已驳回": "err", "已停用": "gray"}[s]
trq = "".join(f"""<tr><td class="num">{a}</td><td>{b}</td><td>{c}</td><td><span class="tag info">{d}</span></td>
<td style="max-width:360px">{e}</td><td class="num">{f:.2f}</td><td class="num">{g:.1f}</td>
<td><span class="tag {qtag(h)}">{h}</span></td><td class="num">{('%.1f%%' % i) if i else '未测'}</td>
<td><button class="btn sm">编辑</button> <button class="btn sm">更多</button></td></tr>""" for a, b, c, d, e, f, g, h, i in qs)
pages["question-list"] = shell("题库列表", "题库列表", mark(ADMIN_NAV)("question-list"), f"""
<div class="card"><div class="card-b"><div class="filter">
<input class="inp" style="min-width:200px" placeholder="题目编号 / 题干关键词">
<select class="inp"><option>全部学科</option><option>高等数学</option><option>数据结构</option></select>
<select class="inp"><option>全部知识点</option><option>换元积分法</option><option>二叉树遍历</option></select>
<select class="inp" style="min-width:130px"><option>全部题型</option><option>单选</option><option>多选</option><option>填空</option></select>
<select class="inp" style="min-width:130px"><option>全部状态</option><option>待审核</option><option>已入库</option><option>已驳回</option></select>
<button class="btn p">查询</button><button class="btn">重置</button>
<button class="btn p" style="margin-left:auto">+ 新增题目</button><button class="btn">批量导入</button></div></div></div>
<div class="card"><div class="card-h"><h2>题目列表</h2><span class="sub">共 2,486 条 · 已选 0 条</span>
<span style="margin-left:auto" class="muted">相似度超过 85% 的题干会在保存时提示合并</span></div>
<table><thead><tr><th>题目编号</th><th>学科</th><th>知识点</th><th>题型</th><th>题干</th><th>难度</th><th>分值</th><th>状态</th><th>正确率</th><th>操作</th></tr></thead>
<tbody>{trq}</tbody></table>
<div class="pager"><span>共 2,486 条</span><b>‹</b><b class="on">1</b><b>2</b><b>3</b><b>…</b><b>249</b><b>›</b><select class="inp" style="min-width:90px;height:28px"><option>10 条/页</option><option>20 条/页</option></select></div></div>""")

# ---------- 6 题目编辑 ----------
pages["question-edit"] = shell("题目编辑", "题库列表 / 题目编辑", mark(ADMIN_NAV)("question-edit"), f"""
<div class="steps"><div class="s on"><span class="n">1</span>录入题干</div><div class="s on"><span class="n">2</span>设置选项与答案</div><div class="s"><span class="n">3</span>解析与知识点</div><div class="s"><span class="n">4</span>提交审核</div></div>
<div class="two">
<div class="card" style="margin:0"><div class="card-h"><h2>录入题目</h2><span class="sub">保存时逐项校验并定位错误行</span></div><div class="card-b">
<div class="form-row"><label>学科</label><div class="ctl"><select class="inp wide"><option>高等数学</option><option>数据结构</option></select></div></div>
<div class="form-row"><label>知识点</label><div class="ctl"><select class="inp wide"><option>一元函数积分学 / 不定积分 / 换元积分法</option></select></div></div>
<div class="form-row"><label>题型</label><div class="ctl"><select class="inp" style="width:140px"><option>单选</option><option>多选</option><option>判断</option><option>填空</option><option>简答</option><option>计算</option></select>
<select class="inp" style="width:120px;margin-left:8px"><option>自建</option><option>真题</option></select></div></div>
<div class="form-row"><label>题干</label><div class="ctl"><textarea class="inp" style="width:100%;height:86px;padding:9px 10px;line-height:1.7;resize:none">计算不定积分 ∫ 2x·cos(x²) dx，并写出所用方法。</textarea>
<div class="muted" style="margin-top:6px">不少于 8 字；公式用文字描述，禁止只放图片</div></div></div>
<div class="form-row"><label>选项</label><div class="ctl">
<div class="opt sel"><span class="lb">A</span><input class="inp" style="flex:1" value="sin(x²) + C"><span class="tag ok">正确</span></div>
<div class="opt"><span class="lb">B</span><input class="inp" style="flex:1" value="2sin(x²) + C"><span class="tag gray">干扰项</span></div>
<div class="opt"><span class="lb">C</span><input class="inp" style="flex:1" value="cos(x²) + C"><span class="tag gray">干扰项</span></div>
<div class="opt"><span class="lb">D</span><input class="inp" style="flex:1" value="x²sin(x²) + C"><span class="tag gray">干扰项</span></div>
<button class="btn sm" style="margin-top:2px">+ 添加选项</button>
<div class="muted" style="margin-top:8px">单选题必须且只能有一个正确项</div></div></div>
<div class="form-row"><label>难度系数</label><div class="ctl"><input class="inp" style="width:100px" value="0.55"><span class="muted" style="margin-left:8px">0.10 - 1.00，可由历史正确率自动校准</span></div></div>
<div class="form-row"><label>分值</label><div class="ctl"><input class="inp" style="width:100px" value="5.0"><span class="muted" style="margin-left:8px">1 - 50 分</span></div></div>
<div class="form-row"><label>解析</label><div class="ctl"><textarea class="inp" style="width:100%;height:66px;padding:9px 10px;line-height:1.7;resize:none">令 u = x²，则 du = 2x dx，原式化为 ∫ cos u du = sin u + C = sin(x²) + C。</textarea>
<div class="muted" style="margin-top:6px">入库时必填，至少 20 字</div></div></div>
<div style="display:flex;gap:8px;margin-left:110px"><button class="btn p">保存草稿</button><button class="btn a">提交审核</button><button class="btn">预览</button></div>
</div></div>
<div class="card" style="margin:0;align-self:start"><div class="card-h"><h2>学生端预览</h2><span class="sub">实时</span></div><div class="card-b">
<div style="display:flex;gap:8px;margin-bottom:12px"><span class="tag info">单选</span><span class="tag gray">难度 0.55</span><span class="tag gray">5.0 分</span><span class="tag gray">换元积分法</span></div>
<div style="font-size:14px;line-height:1.9;margin-bottom:14px">计算不定积分 ∫ 2x·cos(x²) dx，并写出所用方法。</div>
<div class="opt sel"><span class="lb">A</span>sin(x²) + C</div>
<div class="opt"><span class="lb">B</span>2sin(x²) + C</div>
<div class="opt"><span class="lb">C</span>cos(x²) + C</div>
<div class="opt"><span class="lb">D</span>x²sin(x²) + C</div>
<div class="muted" style="margin-top:14px;line-height:1.8">相似度检测：与题干库比对，最高相似度 <b style="color:{C['ok']}">32%</b>，可正常入库。</div>
</div></div></div>""")

# ---------- 7 组卷工作台 ----------
pages["paper-workbench"] = shell("组卷工作台", "组卷工作台", mark(ADMIN_NAV)("paper-workbench"), f"""
<div class="filter" style="margin-bottom:16px">
<input class="inp wide" value="高等数学 期中测评卷 A">
<select class="inp"><option>手动组卷</option><option>随机组卷</option><option>错题重练</option></select>
<select class="inp"><option>建议时长 90 分钟</option><option>60 分钟</option><option>120 分钟</option></select>
<button class="btn">预览试卷</button><button class="btn p">保存试卷</button>
<span class="muted" style="margin-left:auto">总分校验：<b style="color:{C['ok']}">100.0 / 100.0</b></span></div>
<div style="display:grid;grid-template-columns:236px 1fr 340px;gap:16px">
<div class="card" style="margin:0"><div class="card-h"><h2>知识点</h2></div><div class="card-b" style="padding:10px;font-size:12px">
{''.join(f'''<div style="padding:7px 4px;display:flex;align-items:center;gap:8px"><span style="width:14px;height:14px;border-radius:3px;border:1px solid {'#4B3F72' if on else '#C9CED6'};background:{'#4B3F72' if on else '#fff'}"></span>
<span style="flex:1">{n}</span><b class="num" style="font-weight:400;color:{C['muted']}">{q}</b></div>''' for n, q, on in [("函数与极限", 168, 1), ("导数与微分", 214, 1), ("不定积分", 88, 1), ("定积分", 94, 1), ("定积分应用", 54, 0), ("偏导数", 78, 1), ("二重积分", 46, 0)])}
<div style="margin-top:12px;padding-top:12px;border-top:1px solid #EEF0F2">
<div class="muted" style="margin-bottom:6px">抽题数量</div><input class="inp" style="width:100%" value="20">
<div class="muted" style="margin:10px 0 6px">难度区间</div>
<div style="display:flex;gap:6px;align-items:center"><input class="inp" style="width:64px" value="0.30"><span class="muted">—</span><input class="inp" style="width:64px" value="0.80"></div>
<button class="btn p" style="width:100%;margin-top:12px">按权重随机抽题</button></div>
</div></div>
<div class="card" style="margin:0"><div class="card-h"><h2>题目池</h2><span class="sub">已按知识点过滤 · 42 道候选</span>
<span style="margin-left:auto" class="muted">难度均值 0.56</span></div>
<table><thead><tr><th style="width:34px"></th><th>题干</th><th>题型</th><th>难度</th><th>知识点</th><th>操作</th></tr></thead><tbody>
{''.join(f'''<tr><td><span style="display:inline-block;width:14px;height:14px;border-radius:3px;border:1px solid {'#4B3F72' if c else '#C9CED6'};background:{'#4B3F72' if c else '#fff'}"></span></td>
<td style="max-width:340px">{s}</td><td><span class="tag info">{t}</span></td>
<td><span class="tag {'ok' if d < 0.4 else ('warn' if d > 0.7 else 'gray')}">{d}</span></td><td class="muted">{k}</td>
<td><button class="btn sm">{'移出' if c else '加入'}</button></td></tr>''' for s, t, d, k, c in [
  ("计算不定积分 ∫ 2x·cos(x²) dx", "单选", 0.55, "换元积分法", 1),
  ("求函数 y = x³ - 3x 的单调区间与极值", "计算", 0.72, "导数应用", 1),
  ("lim(x→0) (sin 3x)/x 的值为", "填空", 0.35, "两个重要极限", 1),
  ("设 z = x²y + sin(xy)，求全微分 dz", "计算", 0.78, "偏导数", 0),
  ("下列级数中收敛的是", "单选", 0.62, "无穷小比较", 0),
  ("定积分 ∫₀¹ x² dx = ____", "填空", 0.32, "定积分", 1),
  ("函数 f(x)=|x| 在 x=0 处", "单选", 0.44, "函数连续性", 1)])}
</tbody></table></div>
<div class="card" style="margin:0"><div class="card-h"><h2>试卷篮</h2><span class="sub">6 / 20 题</span></div><div class="card-b" style="padding:12px">
<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px">
<div style="background:#F7F5FC;border-radius:8px;padding:10px"><div class="muted">总分</div><b class="num" style="font-size:20px;color:{C['primary']}">100.0</b></div>
<div style="background:#F7F5FC;border-radius:8px;padding:10px"><div class="muted">难度均值</div><b class="num" style="font-size:20px;color:{C['primary']}">0.56</b></div></div>
<div class="h3">题目明细</div>
{''.join(f'''<div style="display:flex;gap:8px;padding:8px 0;border-bottom:1px dashed #EEF0F2;font-size:12px"><b class="num" style="color:{C['muted']}">{i:02d}</b>
<span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{s}</span><span class="num">{sc}</span>
<span style="color:{C['danger']};cursor:pointer">×</span></div>''' for i, (s, sc) in enumerate([("计算不定积分 ∫ 2x·cos(x²) dx", 5.0), ("求函数 y = x³-3x 的单调区间", 12.0), ("lim(x→0)(sin3x)/x 的值", 4.0), ("定积分 ∫₀¹ x² dx", 4.0), ("函数 f(x)=|x| 在 x=0 处", 5.0), ("设 f(x)=x²+2x, 求 f'(1)", 5.0)], 1))}
<div class="muted" style="margin-top:12px;line-height:1.8">知识点覆盖：4 个一级节点 / 6 个三级节点<br>缺口提示：定积分应用题量不足，已按比例回补 2 道相邻知识点题目</div>
<button class="btn p" style="width:100%;margin-top:12px">提交审核并发布</button>
</div></div></div>""")

# ---------- 8 试卷管理 ----------
pl = [("SJ2604010001", "高等数学 期中测评卷 A", "高等数学", "随机", 20, 100.0, 90, "使用中", 386),
      ("SJ2604010002", "数据结构 单元测验（树与图）", "数据结构", "手动", 15, 75.0, 45, "已发布", 214),
      ("SJ2603280007", "线性代数 期末模拟卷", "线性代数", "随机", 22, 110.0, 100, "已归档", 452),
      ("SJ2603250003", "高等数学 错题重练卷（第 3 周）", "高等数学", "错题重练", 10, 50.0, 30, "已发布", 128),
      ("SJ2603200001", "大学物理 电磁学专项", "大学物理", "手动", 18, 90.0, 80, "待审核", 0),
      ("SJ2603180005", "程序设计基础 第 2 章练习", "程序设计基础", "手动", 12, 60.0, 40, "草稿", 0),
      ("SJ2603100002", "高等数学 补考卷", "高等数学", "随机", 20, 100.0, 90, "已驳回", 0)]
def ptag(s):
    return {"使用中": "info", "已发布": "ok", "已归档": "gray", "待审核": "warn", "草稿": "gray", "已驳回": "err"}[s]
pages["paper-list"] = shell("试卷管理", "试卷管理", mark(ADMIN_NAV)("paper-list"), f"""
<div class="card"><div class="card-b"><div class="filter">
<input class="inp" placeholder="试卷编号 / 名称"><select class="inp"><option>全部学科</option></select>
<select class="inp"><option>全部组卷方式</option><option>手动</option><option>随机</option></select>
<select class="inp"><option>全部状态</option><option>已发布</option><option>使用中</option></select>
<button class="btn p">查询</button><button class="btn">重置</button>
<button class="btn p" style="margin-left:auto">+ 新建试卷</button></div></div></div>
<div class="card"><div class="card-h"><h2>试卷列表</h2><span class="sub">共 7 条</span></div>
<table><thead><tr><th>试卷编号</th><th>试卷名称</th><th>学科</th><th>组卷方式</th><th>题数</th><th>总分</th><th>时长</th><th>状态</th><th>作答人次</th><th>操作</th></tr></thead>
<tbody>{''.join(f'''<tr><td class="num">{a}</td><td><b>{b}</b></td><td>{c}</td><td><span class="tag {'info' if d == '随机' else 'gray'}">{d}</span></td>
<td class="num">{e}</td><td class="num">{f}</td><td class="num">{g} 分钟</td><td><span class="tag {ptag(h)}">{h}</span></td><td class="num">{i}</td>
<td><button class="btn sm">查看</button> <button class="btn sm">覆盖度</button> <button class="btn sm">更多</button></td></tr>''' for a, b, c, d, e, f, g, h, i in pl)}</tbody></table>
<div class="pager"><span>共 7 条</span><b class="on">1</b><select class="inp" style="min-width:90px;height:28px"><option>10 条/页</option></select></div></div>""")

# ---------- 9 审核台 ----------
pages["audit"] = shell("题目审核台", "题目审核台", mark(ADMIN_NAV)("audit"), f"""
<div class="filter" style="margin-bottom:16px">
<select class="inp"><option>全部学科</option></select><select class="inp" style="min-width:130px"><option>全部题型</option></select>
<input class="inp" placeholder="提交人"><button class="btn p">筛选</button>
<span class="tag warn" style="margin-left:auto">待审核 37 条 · 超时 4 条</span></div>
<div style="display:grid;grid-template-columns:260px 1fr 320px;gap:16px">
<div class="card" style="margin:0"><div class="card-h"><h2>待审核队列</h2></div><div style="padding:6px">
{''.join(f'''<div style="padding:11px;border-radius:8px;{'background:#F7F5FC;border-left:3px solid #4B3F72' if i == 0 else ''};border-bottom:1px solid #F2F4F6">
<div style="display:flex;justify-content:space-between;font-size:12px"><b>{n}</b><span class="muted">{t}</span></div>
<div style="font-size:11px;color:{C['muted']};margin-top:4px">{s} · {u} · {d}</div></div>''' for i, (n, t, s, u, d) in enumerate([
  ("TM01000004", "填空", "高等数学", "王振", "2 小时前"), ("TM01000011", "单选", "数据结构", "赵磊", "5 小时前"),
  ("TM01000012", "简答", "高等数学", "王振", "昨天"), ("TM02000008", "多选", "线性代数", "周敏", "昨天"),
  ("TM03000021", "计算", "大学物理", "周敏", "2 天前")]))}
</div></div>
<div class="card" style="margin:0"><div class="card-h"><h2>题干与选项预览</h2><span class="sub">TM01000004 · 第 1 次提交</span></div><div class="card-b">
<div style="display:flex;gap:8px;margin-bottom:14px"><span class="tag info">填空</span><span class="tag gray">难度 0.35</span><span class="tag gray">4.0 分</span><span class="tag gray">自建</span></div>
<div style="font-size:15px;line-height:1.9;padding:14px;background:#FAFBFC;border-radius:8px">lim(x→0) sin x / x = ____</div>
<div class="h3" style="margin-top:18px">标准答案</div>
<div style="padding:12px;border:1px solid #C6E0D3;background:#EAF4EF;border-radius:8px;font-size:13px">1</div>
<div class="h3" style="margin-top:18px">解析</div>
<div style="font-size:13px;line-height:1.9;color:#3D4752">由重要极限 lim(x→0) sin x / x = 1 直接得到。该极限是等价无穷小 sin x ~ x 的来源，常用于替换化简。<br><span class="tag info" style="margin-top:8px">字数 62 / 要求 ≥ 20</span></div>
<div class="h3" style="margin-top:18px">历史审核记录</div>
<div class="muted" style="line-height:1.9">2026-10-28 14:22 王振 提交审核<br>2026-10-28 16:05 李静 通过（首次入库）</div>
</div></div>
<div class="card" style="margin:0;align-self:start"><div class="card-h"><h2>归类与校准</h2></div><div class="card-b">
<div class="form-row"><label style="width:76px">知识点</label><div class="ctl"><select class="inp" style="width:100%"><option>函数与极限 / 两个重要极限</option></select></div></div>
<div class="form-row"><label style="width:76px">难度</label><div class="ctl"><input class="inp" style="width:100%" value="0.35"></div></div>
<div class="form-row"><label style="width:76px">来源</label><div class="ctl"><select class="inp" style="width:100%"><option>自建</option><option>真题</option></select></div></div>
<div class="form-row"><label style="width:76px">重复度</label><div class="ctl"><span class="tag ok">12% · 无重复</span></div></div>
<div class="h3" style="margin-top:6px">退回原因（退回时必填）</div>
<select class="inp" style="width:100%;margin-bottom:8px"><option>题干不清</option><option>答案错误</option><option>解析缺失</option><option>知识点错误</option></select>
<textarea class="inp" style="width:100%;height:64px;padding:9px;resize:none" placeholder="补充说明（5-200 字）"></textarea>
<div style="display:flex;gap:8px;margin-top:14px"><button class="btn p" style="flex:1">通过入库</button><button class="btn d" style="flex:1">退回修改</button></div>
<div class="muted" style="margin-top:12px;line-height:1.8">规则：审核人不得为创建人；退回原因将写入操作日志并通知提交人。</div>
</div></div></div>""")

# ---------- 10 批量导入 ----------
pages["import"] = shell("批量导入", "批量导入", mark(ADMIN_NAV)("import"), f"""
<div class="grid" style="grid-template-columns:1fr 380px">
<div class="card" style="margin:0"><div class="card-h"><h2>Excel 批量导入题目</h2><span class="sub">异步执行，逐行校验</span></div><div class="card-b">
<div style="border:1px dashed #C9CED6;border-radius:10px;padding:34px;text-align:center;background:#FCFCFD">
<div style="font-size:30px;color:{C['sub']}">⬆</div>
<div style="margin:10px 0 6px;font-size:13px">把 .xlsx 文件拖到这里，或 <span style="color:{C['primary']};font-weight:600">点击选择</span></div>
<div class="muted">限 1 个文件，不超过 10 MB，单次最多 500 行</div>
<button class="btn" style="margin-top:14px">下载导入模板</button></div>
<div class="h3" style="margin-top:20px">校验规则</div>
<div class="muted" style="line-height:2">
① 题型只能是 单选/多选/判断/填空/简答/计算<br>
② 单选题必须有且仅有 1 个正确项，多选题至少 2 个<br>
③ 答案格式：单选 A、多选 A,C（升序）、判断 对/错<br>
④ 知识点编码必须存在于所选学科的启用节点<br>
⑤ 题干不少于 8 字，解析不少于 20 字</div>
</div></div>
<div class="card" style="margin:0;align-self:start"><div class="card-h"><h2>最近导入任务</h2></div><div class="card-b" style="padding:0">
{''.join(f'''<div style="padding:12px 16px;border-bottom:1px solid #F2F4F6">
<div style="display:flex;justify-content:space-between;font-size:12px"><b>{f}</b><span class="tag {t}">{s}</span></div>
<div class="muted" style="margin-top:5px">{d} · 成功 {ok} / 失败 {bad}</div>
<div class="bar" style="margin-top:7px"><i class="{'ok' if bad == 0 else 'a'}" style="width:{p}%"></i></div></div>''' for f, s, t, d, ok, bad, p in [
  ("高数_第5章_积分.xlsx", "已完成", "ok", "2026-10-30 09:12", 118, 2, 100),
  ("数据结构_树与图.xlsx", "已完成", "ok", "2026-10-29 15:40", 64, 0, 100),
  ("线代_矩阵.xlsx", "部分失败", "warn", "2026-10-28 11:03", 39, 11, 78),
  ("物理_电磁学.xlsx", "执行中", "info", "刚刚", 0, 0, 22)])}
<div style="padding:14px 16px"><button class="btn" style="width:100%">下载失败行明细</button></div>
</div></div></div>""")

# ---------- 11 学情诊断（教师） ----------
pages["mastery"] = shell("学情诊断", "学情诊断", mark(ADMIN_NAV)("mastery"), f"""
<div class="filter" style="margin-bottom:16px">
<select class="inp"><option>高等数学</option><option>数据结构</option></select>
<select class="inp"><option>计算机 2301 班</option><option>计算机 2302 班</option></select>
<select class="inp"><option>最近 30 天</option><option>本学期</option></select>
<button class="btn p">查询</button><button class="btn">重新计算</button>
<span class="muted" style="margin-left:auto">规则版本 v3 · 上次重算 2026-11-01 02:00</span></div>
<div class="grid" style="grid-template-columns:1fr 1.25fr">
<div class="card" style="margin:0"><div class="card-h"><h2>知识点掌握度雷达</h2><span class="sub">班级均值</span></div>
<div class="card-b"><div class="chart" style="height:280px">六维雷达：函数与极限 78 / 导数与微分 71 / 不定积分 54 / 定积分 62 / 偏导数 66 / 常微分方程 48</div></div></div>
<div class="card" style="margin:0"><div class="card-h"><h2>薄弱知识点清单</h2><span class="sub">掌握度低于 70 共 5 项</span>
<span style="margin-left:auto"><button class="btn sm a">一键生成专项练习</button></span></div>
<table><thead><tr><th>知识点</th><th>掌握度</th><th>样本量</th><th>主要失分因素</th><th>结论</th></tr></thead><tbody>
{''.join(f'''<tr><td><b>{n}</b></td><td><div style="display:flex;align-items:center;gap:8px"><div class="bar" style="width:74px"><i class="{'d' if v < 50 else 'a'}" style="width:{v}%"></i></div><b class="num">{v}</b></div></td>
<td class="num">{s}</td><td class="muted">{f}</td><td><span class="tag {t}">{c}</span></td></tr>''' for n, v, s, f, c, t in [
  ("换元积分法", 42, 86, "正确率 41% · 重做失败 12 次", "严重薄弱", "err"),
  ("分部积分法", 47, 62, "耗时超标准 1.8 倍", "严重薄弱", "err"),
  ("定积分应用", 51, 48, "正确率 54% · 复习不及时", "薄弱", "warn"),
  ("特征值与特征向量", 58, 34, "重做正确率 60%", "薄弱", "warn"),
  ("偏导数与全微分", 66, 92, "正确率 71%，稳定", "基本掌握", "gray")])}
</tbody></table>
<div class="muted" style="padding:12px 16px">样本少于 5 次的知识点标注「数据不足」，不参与薄弱排名。</div></div></div>
<div class="card"><div class="card-h"><h2>掌握度计算留痕</h2><span class="sub">相同输入与规则版本必须得到相同结果</span></div>
<div class="card-b" style="padding:0">
<table><thead><tr><th>知识点</th><th>正确率 40%</th><th>耗时 15%</th><th>重做 20%</th><th>考纲权重 15%</th><th>复习及时率 10%</th><th>加权总分</th><th>等级</th></tr></thead><tbody>
<tr><td><b>换元积分法</b></td><td class="num">41.0 → 41</td><td class="num">0.0 → 22</td><td class="num">46.0 → 46</td><td class="num">4.0 → 40</td><td class="num">0 → 0</td><td><b class="num" style="color:{C['danger']}">32.7</b></td><td><span class="tag err">严重薄弱</span></td></tr>
<tr><td>分部积分法</td><td class="num">52.0 → 52</td><td class="num">0.0 → 18</td><td class="num">50.0 → 50</td><td class="num">3.0 → 30</td><td class="num">40 → 40</td><td><b class="num">38.1</b></td><td><span class="tag err">严重薄弱</span></td></tr>
<tr><td>定积分</td><td class="num">68.0 → 68</td><td class="num">0.72 → 72</td><td class="num">70.0 → 70</td><td class="num">12.0 → 100</td><td class="num">60 → 60</td><td><b class="num">71.0</b></td><td><span class="tag warn">基本掌握</span></td></tr>
<tr><td>偏导数与全微分</td><td class="num">82.0 → 82</td><td class="num">0.88 → 88</td><td class="num">70.0 → 70</td><td class="num">9.0 → 75</td><td class="num">80 → 80</td><td><b class="num" style="color:{C['ok']}">80.9</b></td><td><span class="tag ok">基本掌握</span></td></tr>
</tbody></table></div></div>
<div class="card"><div class="card-h"><h2>诊断结论与人工修正</h2><span class="sub">修正需填写不少于 5 字原因，原始结果保留</span></div>
<div class="card-b two">
<div><div class="h3">系统结论</div>
<div style="font-size:13px;line-height:2">等级：<b style="color:{C['danger']}">严重薄弱</b>（32.7 分，低于 50 分档）<br>
主要影响因素：近 30 天正确率仅 41%（贡献失分 23.6）、平均耗时达标准时长 2.3 倍（贡献失分 12）<br>
未满足条件：错题连续答对未达 2 次；1 天/3 天/7 天复习计划完成 0 项<br>
可改进项：先重做 8 道换元积分基础题；为错题建立 1-3-7 复习计划；变式题推送 3 道</div>
<div style="margin-top:14px;display:flex;gap:8px"><button class="btn a">采纳结论并推送练习</button><button class="btn">人工修正</button></div></div>
<div style="border-left:1px solid #EEF0F2;padding-left:20px"><div class="h3">修正记录</div>
<div class="muted" style="line-height:2">2026-10-30 09:14 李静：该班刚上完换元法第 2 课时，样本偏少 → 修正为「薄弱」<br>原因：教学进度滞后导致正确率偏低，非掌握问题<br>
2026-10-26 16:40 王振：维持系统结论</div>
<div style="margin-top:14px;background:#FDF3E3;border:1px solid #F0D9B0;border-radius:8px;padding:12px;font-size:12px;line-height:1.9">
<b>修正率统计</b><br>本月诊断 486 条 · 人工修正 37 条（7.6%）· 修正后练习完成率 82%</div></div></div></div>""")

# ---------- 12 学生端：练习中心 ----------
pages["practice-center"] = portal("练习中心", "practice-center", f"""
<div style="display:flex;align-items:flex-end;gap:14px;margin-bottom:18px">
<div><div style="font-size:20px;font-weight:700">练习中心</div><div class="muted" style="margin-top:6px">按学科与知识点推荐，交卷即生成错题</div></div>
<div style="margin-left:auto" class="filter"><select class="inp"><option>全部学科</option></select><button class="btn p">开始学习</button></div></div>
<div class="kpi" style="grid-template-columns:repeat(4,1fr);margin-bottom:18px">
<div class="k"><div class="t">待完成练习</div><div class="v num">3</div><div class="d">1 份将于今晚截止</div></div>
<div class="k"><div class="t">本周练习</div><div class="v num">7</div><div class="d">累计 142 分钟</div></div>
<div class="k"><div class="t">平均正确率</div><div class="v num">76.2%</div><div class="d">较上周 +4.5pt</div></div>
<div class="k"><div class="t">待复习错题</div><div class="v num">12</div><div class="d">今日到期 4 道</div></div></div>
<div class="h3">教师布置的练习</div>
<div class="grid" style="grid-template-columns:repeat(3,1fr);margin-bottom:20px">
{''.join(f'''<div class="card" style="margin:0"><div class="card-b">
<div style="display:flex;justify-content:space-between;align-items:center"><span class="tag info">{t}</span><span class="muted">{d}</span></div>
<div style="font-size:14px;font-weight:600;margin:10px 0 6px">{n}</div>
<div class="muted">{s} · {q} 题 · 预计 {m} 分钟</div>
<div style="display:flex;justify-content:space-between;align-items:center;margin-top:14px">
<span class="tag {'err' if u else 'warn'}">{'今日截止' if u else '进行中'}</span><button class="btn p sm">开始答题</button></div>
</div></div>''' for t, n, s, q, m, d, u in [
  ("试卷练习", "高等数学 期中测评卷 A", "高等数学", 20, 90, "王振 布置", 1),
  ("知识点练习", "换元积分法专项巩固", "高等数学", 10, 25, "系统推荐", 0),
  ("错题重练", "错题重练（第 3 周）", "高等数学", 10, 20, "李静 布置", 0)])}</div>
<div class="h3">继续上次练习</div>
<div class="card" style="margin:0"><div class="card-b" style="display:flex;align-items:center;gap:18px">
<div style="width:44px;height:44px;border-radius:10px;background:#F0EEF7;display:flex;align-items:center;justify-content:center;font-size:18px">✎</div>
<div style="flex:1"><div style="font-weight:600">数据结构 单元测验（树与图）</div><div class="muted" style="margin-top:4px">已答 9/15 题 · 剩余 26 分钟 · 上次保存 12:41</div>
<div class="bar" style="margin-top:8px;max-width:420px"><i style="width:60%"></i></div></div>
<button class="btn p">继续答题</button></div></div>""")

# ---------- 13 学生端：答题页 ----------
pages["answer"] = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><title>答题 · 智汇题库</title><style>{CSS % C}
body{{background:#F5F6F7}}
.hd{{height:56px;background:#fff;border-bottom:1px solid #E4E7EB;display:flex;align-items:center;padding:0 28px;gap:16px}}
.hd .ttl{{font-size:14px;font-weight:600}}
.timer{{margin-left:auto;display:flex;align-items:center;gap:8px;font-size:13px}}
.timer b{{font-size:18px;color:{C['primary']}}}
.qcard{{background:#fff;border-radius:10px;border:1px solid #E4E7EB;padding:26px 30px}}
</style></head><body>
<div class="hd"><div class="ttl">高等数学 期中测评卷 A</div><span class="tag info">试卷练习</span>
<div class="timer">剩余时间 <b class="num">68:24</b><span class="muted">/ 90 分钟</span></div>
<button class="btn">保存</button><button class="btn p">交卷</button></div>
<div style="display:grid;grid-template-columns:1fr 268px;gap:16px;max-width:1180px;margin:20px auto;padding:0 20px">
<div><div class="bar" style="margin-bottom:14px"><i class="a" style="width:35%"></i></div>
<div class="muted" style="margin-bottom:12px">第 7 / 20 题 · 已答 6 题 · 未答 14 题</div>
<div class="qcard"><div style="display:flex;gap:8px;margin-bottom:16px"><span class="tag info">单选题</span><span class="tag gray">5.0 分</span><span class="tag gray">难度 0.55</span></div>
<div style="font-size:16px;line-height:1.9;margin-bottom:20px">计算不定积分 ∫ 2x·cos(x²) dx，正确结果是（ ）</div>
<div class="opt sel"><span class="lb">A</span>sin(x²) + C</div>
<div class="opt"><span class="lb">B</span>2sin(x²) + C</div>
<div class="opt"><span class="lb">C</span>cos(x²) + C</div>
<div class="opt"><span class="lb">D</span>x²sin(x²) + C</div>
<div style="display:flex;gap:10px;margin-top:22px"><button class="btn">上一题</button><button class="btn">标记待定</button><button class="btn p" style="margin-left:auto">下一题</button></div>
</div></div>
<div><div class="card" style="margin:0"><div class="card-h"><h2>答题卡</h2></div><div class="card-b">
<div class="muted" style="margin-bottom:8px">一、单选题（1-10）</div>
<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:7px">
{''.join(f'<div style="height:30px;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:12px;border:1px solid {"#4B3F72" if s == "on" else ("#C6E0D3" if s == "done" else "#E4E7EB")};background:{"#4B3F72" if s == "on" else ("#EAF4EF" if s == "done" else "#fff")};color:{"#fff" if s == "on" else ("#2B7955" if s == "done" else "#5B6770")}">{i}</div>' for i, s in enumerate(["done", "done", "done", "done", "done", "done", "on", "", "", ""], 1))}
</div>
<div class="muted" style="margin:14px 0 8px">二、多选题（11-14）</div>
<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:7px">
{''.join(f'<div style="height:30px;border-radius:6px;border:1px solid #E4E7EB;display:flex;align-items:center;justify-content:center;font-size:12px;color:#5B6770">{i}</div>' for i in range(11, 15))}
</div>
<div class="muted" style="margin:14px 0 8px">三、填空与计算（15-20）</div>
<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:7px">
{''.join(f'<div style="height:30px;border-radius:6px;border:1px solid #E4E7EB;display:flex;align-items:center;justify-content:center;font-size:12px;color:#5B6770">{i}</div>' for i in range(15, 21))}
</div>
<div style="margin-top:16px;display:flex;gap:10px;font-size:11px;color:{C['muted']}"><span>■ 已答</span><span style="color:#4B3F72">■ 当前</span><span>□ 未答</span></div>
</div></div>
<div class="card" style="margin-top:14px"><div class="card-b muted" style="line-height:1.9">
交卷后客观题即时判分，填空按去空格比对，简答按关键词命中给分。同一练习重复提交返回首次判分结果。</div></div></div></div></body></html>"""

# ---------- 14 学生端：错题本 ----------
wb = [("计算不定积分 ∫ 2x·cos(x²) dx", "高等数学", "换元积分法", 3, "2026-10-30 20:14", "未掌握"),
      ("求函数 y = x³-3x 的单调区间与极值", "高等数学", "导数应用", 2, "2026-10-29 19:02", "复习中"),
      ("对二叉树进行中序遍历，得到的序列", "数据结构", "二叉树遍历", 4, "2026-10-28 21:40", "未掌握"),
      ("定积分 ∫₀¹ x² dx 的值为", "高等数学", "定积分", 1, "2026-10-27 15:22", "已掌握"),
      ("lim(x→0) sin3x/x 的值为", "高等数学", "两个重要极限", 2, "2026-10-26 10:08", "已掌握"),
      ("简述指针与引用的区别", "数据结构", "指针与引用", 1, "2026-10-25 16:35", "复习中")]
pages["wrong-book"] = portal("我的错题本", "wrong-book", f"""
<div style="display:flex;align-items:flex-end;margin-bottom:16px">
<div><div style="font-size:20px;font-weight:700">我的错题本</div><div class="muted" style="margin-top:6px">共 12 道待复习 · 今日到期 4 道</div></div>
<div style="margin-left:auto;display:flex;gap:8px"><button class="btn">按 1-3-7 计划复习</button><button class="btn p">开始错题重练</button></div></div>
<div class="card" style="margin-bottom:16px"><div class="card-b"><div class="filter">
<select class="inp"><option>全部学科</option><option>高等数学</option><option>数据结构</option></select>
<select class="inp"><option>全部知识点</option></select>
<select class="inp" style="min-width:140px"><option>全部掌握状态</option><option>未掌握</option><option>复习中</option><option>已掌握</option></select>
<input class="inp" placeholder="题干关键词"><button class="btn p">筛选</button><button class="btn">重置</button></div></div></div>
<div style="display:grid;grid-template-columns:1fr 400px;gap:16px;align-items:start">
<div class="card" style="margin:0"><div class="card-h"><h2>错题列表</h2><span class="sub">同一题目仅保留一条并累加错误次数</span></div>
<table><thead><tr><th>题干</th><th>学科</th><th>知识点</th><th>错误次数</th><th>最近错误</th><th>状态</th><th>操作</th></tr></thead><tbody>
{''.join(f'''<tr><td style="max-width:260px">{s}</td><td>{sub}</td><td class="muted">{k}</td>
<td><b class="num" style="color:{C['danger']}">{c}</b></td><td class="num muted">{t}</td>
<td><span class="tag {'err' if st == '未掌握' else ('warn' if st == '复习中' else 'ok')}">{st}</span></td>
<td><button class="btn sm">详情</button> <button class="btn sm">重练</button></td></tr>''' for s, sub, k, c, t, st in wb)}
</tbody></table></div>
<div class="card" style="margin:0"><div class="card-h"><h2>错题详情</h2><span class="sub">原题与解析</span></div><div class="card-b">
<div style="display:flex;gap:8px;margin-bottom:12px"><span class="tag info">单选</span><span class="tag gray">换元积分法</span><span class="tag err">错误 3 次</span></div>
<div style="font-size:14px;line-height:1.9;margin-bottom:14px">计算不定积分 ∫ 2x·cos(x²) dx，正确结果是（ ）</div>
<div class="opt"><span class="lb">A</span><span style="flex:1">sin(x²) + C</span><span class="tag ok">正确答案</span></div>
<div class="opt" style="border-color:{C['danger']};background:#FBEBED"><span class="lb" style="background:{C['danger']};border-color:{C['danger']};color:#fff">B</span><span style="flex:1">2sin(x²) + C</span><span class="tag err">我的作答</span></div>
<div class="opt"><span class="lb">C</span><span style="flex:1">cos(x²) + C</span></div>
<div class="opt"><span class="lb">D</span><span style="flex:1">x²sin(x²) + C</span></div>
<div class="h3" style="margin-top:16px">解析</div>
<div style="font-size:13px;line-height:1.9;background:#FAFBFC;padding:12px;border-radius:8px">令 u = x²，则 du = 2x dx，原式化为 ∫ cos u du = sin u + C，回代得 sin(x²) + C。易错点：忘记回代或把系数误乘 2。</div>
<div class="h3" style="margin-top:14px">复习计划</div>
<div class="muted" style="line-height:2">第 1 天 2026-10-31 ✓ 已重做（错）<br>第 3 天 2026-11-02 待复习<br>第 7 天 2026-11-06 未开始</div>
<div style="display:flex;gap:8px;margin-top:14px"><button class="btn p" style="flex:1">立即重练</button><button class="btn" style="flex:1">填写错因</button></div>
<div class="muted" style="margin-top:10px">连续答对 2 次自动转为「已掌握」，答错则连续次数归零。</div>
</div></div></div>""")

# ---------- 15 学生端：我的学情诊断 ----------
pages["mastery-student"] = portal("我的学情诊断", "mastery-student", f"""
<div style="display:flex;align-items:flex-end;margin-bottom:16px">
<div><div style="font-size:20px;font-weight:700">我的学情诊断</div><div class="muted" style="margin-top:6px">数据截至 2026-11-01 02:00 · 样本 128 次作答</div></div>
<div style="margin-left:auto"><button class="btn">查看计算口径</button></div></div>
<div class="kpi" style="grid-template-columns:repeat(4,1fr);margin-bottom:16px">
<div class="k"><div class="t">综合掌握度</div><div class="v num">71.4</div><div class="d">基本掌握</div></div>
<div class="k"><div class="t">已掌握知识点</div><div class="v num">9</div><div class="d">共 18 个已测</div></div>
<div class="k"><div class="t">薄弱知识点</div><div class="v num">4</div><div class="d">2 个严重薄弱</div></div>
<div class="k"><div class="t">错题转化率</div><div class="v num">58%</div><div class="d">近 30 天</div></div></div>
<div class="grid" style="grid-template-columns:1fr 1.2fr;margin-bottom:16px">
<div class="card" style="margin:0"><div class="card-h"><h2>知识点掌握度</h2><span class="sub">高等数学</span></div>
<div class="card-b"><div class="chart" style="height:270px">雷达图：函数与极限 82 / 导数与微分 76 / 不定积分 42 / 定积分 68 / 偏导数 74 / 常微分方程 49</div></div></div>
<div class="card" style="margin:0"><div class="card-h"><h2>薄弱知识点与推荐</h2></div>
<table><thead><tr><th>知识点</th><th>掌握度</th><th>样本</th><th>结论</th><th>推荐</th></tr></thead><tbody>
{''.join(f'''<tr><td><b>{n}</b></td><td><div style="display:flex;align-items:center;gap:7px"><div class="bar" style="width:60px"><i class="{'d' if v < 50 else 'a'}" style="width:{v}%"></i></div><b class="num">{v}</b></div></td>
<td class="num">{s}</td><td><span class="tag {t}">{r}</span></td><td><button class="btn sm p">练 10 题</button></td></tr>''' for n, v, s, r, t in [
  ("换元积分法", 42, 12, "严重薄弱", "err"), ("分部积分法", 47, 8, "严重薄弱", "err"),
  ("常微分方程", 49, 6, "严重薄弱", "err"), ("定积分应用", 58, 9, "薄弱", "warn"),
  ("函数与极限", 82, 26, "已掌握", "ok")])}
</tbody></table>
<div class="muted" style="padding:12px 16px;line-height:1.8">样本少于 5 次标注「数据不足」，不参与薄弱排名。诊断结论每日凌晨重算一次。</div></div></div>
<div class="card" style="margin:0"><div class="card-h"><h2>本周建议动作</h2></div><div class="card-b" style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px">
{''.join(f'''<div style="border:1px solid #E4E7EB;border-radius:9px;padding:14px">
<div style="font-size:12px;color:{C['muted']}">{k}</div><div style="font-weight:600;margin:7px 0 5px">{t}</div>
<div class="muted" style="line-height:1.7">{d}</div><button class="btn sm p" style="margin-top:10px">去完成</button></div>''' for k, t, d in [
  ("今日到期", "4 道错题复习", "换元积分法 2 道、二叉树遍历 1 道、定积分 1 道"),
  ("系统推荐", "换元积分法专项 10 题", "按薄弱知识点生成，预计 22 分钟"),
  ("计划提醒", "建立 1-3-7 复习计划", "3 道错题尚未建计划，及时率按 0 分计")])}</div></div>""")

# ---------- 16 班级学情 ----------
pages["class-stat"] = shell("班级学情", "班级学情", mark(ADMIN_NAV)("class-stat"), f"""
<div class="filter" style="margin-bottom:16px"><select class="inp"><option>计算机 2301 班</option><option>计算机 2302 班</option></select>
<select class="inp"><option>高等数学</option></select><select class="inp"><option>最近 30 天</option></select>
<button class="btn p">查询</button><button class="btn">导出统计</button>
<span class="muted" style="margin-left:auto">参与率 92.4% · 平均正确率 72.4%</span></div>
<div class="grid" style="grid-template-columns:1.4fr 1fr">
<div class="card" style="margin:0"><div class="card-h"><h2>学生掌握度排名</h2><span class="sub">支持下钻个人诊断</span></div>
<table><thead><tr><th>排名</th><th>学号</th><th>姓名</th><th>练习次数</th><th>平均正确率</th><th>综合掌握度</th><th>薄弱知识点</th><th>操作</th></tr></thead><tbody>
{''.join(f'''<tr><td class="num">{r}</td><td class="num">{sid}</td><td><b>{n}</b></td><td class="num">{c}</td><td class="num">{a}%</td>
<td><div style="display:flex;align-items:center;gap:7px"><div class="bar" style="width:60px"><i class="{'ok' if m >= 85 else ('a' if m < 60 else '')}" style="width:{m}%"></i></div><b class="num">{m}</b></div></td>
<td class="muted">{w}</td><td><button class="btn sm">诊断</button></td></tr>''' for r, sid, n, c, a, m, w in [
  (1, "2023010122", "周雨桐", 18, 91.2, 88, "无"), (2, "2023010101", "陈皓", 16, 84.6, 82, "常微分方程"),
  (3, "2023010145", "林一鸣", 15, 78.3, 74, "定积分应用"), (4, "2023010108", "张梓睿", 14, 71.5, 68, "换元积分法"),
  (5, "2023010119", "何书瑶", 13, 68.9, 61, "换元积分法、分部积分法"),
  (6, "2023010133", "刘泽宇", 12, 62.4, 54, "分部积分法、常微分方程"),
  (7, "2023010107", "吴思远", 11, 58.1, 47, "换元积分法、定积分应用")])}
</tbody></table>
<div class="pager"><span>共 42 名学生</span><b class="on">1</b><b>2</b><b>3</b><b>›</b></div></div>
<div class="card" style="margin:0"><div class="card-h"><h2>班级薄弱知识点热力</h2><span class="sub">行=知识点，列=学生分组</span></div>
<div class="card-b"><div class="chart" style="height:240px">热力图：7 个知识点 × 6 个小组，颜色越深掌握度越低</div>
<div class="h3" style="margin-top:16px">一键专项练习</div>
<div class="muted" style="line-height:1.9">选中「换元积分法」「分部积分法」共影响 23 名学生，生成 10 题专项卷并推送。</div>
<div style="display:flex;gap:8px;margin-top:12px"><button class="btn p" style="flex:1">生成并推送</button><button class="btn">选择学生</button></div></div></div></div>""")

# ---------- 17 用户与角色 ----------
pages["user-role"] = shell("用户与角色", "用户与角色", mark(ADMIN_NAV)("user-role"), f"""
<div class="card"><div class="card-b"><div class="filter">
<input class="inp" placeholder="账号 / 姓名"><select class="inp"><option>全部角色</option><option>学生</option><option>任课教师</option><option>教研员</option><option>教学秘书</option><option>系统管理员</option></select>
<select class="inp"><option>全部状态</option></select><button class="btn p">查询</button>
<button class="btn p" style="margin-left:auto">+ 新建用户</button><button class="btn">角色管理</button><button class="btn">菜单管理</button></div></div></div>
<div class="grid" style="grid-template-columns:1fr 340px">
<div class="card" style="margin:0"><div class="card-h"><h2>用户列表</h2><span class="sub">共 486 条</span></div>
<table><thead><tr><th>账号</th><th>姓名</th><th>角色</th><th>部门</th><th>数据范围</th><th>状态</th><th>最近登录</th><th>操作</th></tr></thead><tbody>
{''.join(f'''<tr><td class="num">{a}</td><td><b>{n}</b></td><td><span class="tag {t}">{r}</span></td><td>{d}</td><td class="muted">{s}</td>
<td><span class="tag {'ok' if st == '正常' else 'gray'}">{st}</span></td><td class="num muted">{l}</td>
<td><button class="btn sm">编辑</button> <button class="btn sm">重置密码</button></td></tr>''' for a, n, r, t, d, s, st, l in [
  ("admin", "系统管理员", "系统管理员", "info", "教务处", "全部", "正常", "2026-11-01 06:40"),
  ("auditor", "李静", "教研员", "warn", "数学教研室", "本部门", "正常", "2026-11-01 07:02"),
  ("teacher01", "王振", "任课教师", "ok", "计算机学院", "本部门", "正常", "2026-10-31 21:18"),
  ("secretary", "赵敏", "教学秘书", "gray", "教务处", "全部", "正常", "2026-10-31 17:44"),
  ("2023010101", "陈皓", "学生", "gray", "计算机 2301", "本人", "正常", "2026-11-01 08:12"),
  ("2023010122", "周雨桐", "学生", "gray", "计算机 2301", "本人", "正常", "2026-10-31 22:05")])}
</tbody></table>
<div class="pager"><span>共 486 条</span><b class="on">1</b><b>2</b><b>…</b><b>49</b><b>›</b></div></div>
<div class="card" style="margin:0;align-self:start"><div class="card-h"><h2>为角色分配菜单</h2></div><div class="card-b">
<div class="form-row"><label style="width:70px">角色</label><div class="ctl"><select class="inp" style="width:100%"><option>教研员</option><option>任课教师</option><option>学生</option></select></div></div>
<div style="border:1px solid #E4E7EB;border-radius:8px;padding:12px;font-size:12px;line-height:2.1">
<div><span style="color:#4B3F72">▾</span> <b>题库中心</b></div>
<div style="padding-left:20px"><span style="color:#4B3F72">☑</span> 题库统计首页　<span style="color:#4B3F72">☑</span> 学科管理</div>
<div style="padding-left:20px"><span style="color:#4B3F72">☑</span> 知识点树　<span style="color:#4B3F72">☑</span> 题库列表</div>
<div style="padding-left:20px"><span style="color:#4B3F72">☑</span> 题目编辑　<span style="color:#4B3F72">☑</span> 题目审核台</div>
<div><span style="color:#4B3F72">▾</span> <b>组卷与练习</b></div>
<div style="padding-left:20px"><span style="color:#4B3F72">☑</span> 组卷工作台　<span style="color:#4B3F72">☑</span> 试卷管理</div>
<div style="padding-left:20px"><span>☐</span> 练习中心（学生专属）</div>
<div><span style="color:#4B3F72">▾</span> <b>系统管理</b></div>
<div style="padding-left:20px"><span>☐</span> 用户与角色　<span>☐</span> 操作日志</div>
</div>
<div style="display:flex;gap:8px;margin-top:14px"><button class="btn p" style="flex:1">保存授权</button><button class="btn">重置</button></div>
<div class="muted" style="margin-top:12px;line-height:1.8">角色权限按「菜单 + 按钮 + 数据范围」三层控制，写接口后端复核。</div>
</div></div></div>""")

# ---------- 18 规则配置 ----------
pages["rule-config"] = shell("诊断规则配置", "诊断规则配置", mark(ADMIN_NAV)("rule-config"), f"""
<div class="filter" style="margin-bottom:16px"><span class="tag info">当前生效 v3</span>
<span class="muted">生效时间 2026-10-01 00:00 · 历史计算按 v2 口径保留</span>
<button class="btn p" style="margin-left:auto">保存并发布 v4</button></div>
<div class="grid" style="grid-template-columns:1.3fr 1fr">
<div class="card" style="margin:0"><div class="card-h"><h2>五项因子权重</h2><span class="sub">合计必须等于 100%</span>
<span style="margin-left:auto;font-size:13px">合计 <b style="color:{C['ok']}">100%</b></span></div>
<table><thead><tr><th>因子</th><th>数据来源</th><th>权重</th><th>缺失处理</th></tr></thead><tbody>
{''.join(f'''<tr><td><b>{n}</b></td><td class="muted">{s}</td><td><input class="inp num" style="width:78px" value="{w}"> <span class="muted">%</span></td><td class="muted">{m}</td></tr>''' for n, s, w, m in [
  ("近30天正确率", "practice_record 按知识点汇总", "40", "无作答标记未测，不参与排名"),
  ("平均答题耗时比", "题目平均用时 / 建议时长", "15", "无记录记 0 分，超 2 倍记 0"),
  ("错题重做表现", "wrong_book 重练记录", "20", "无错题按 70 分基准"),
  ("考纲权重", "knowledge_point.exam_weight", "15", "缺失按一级节点均值"),
  ("复习及时率", "1/3/7 天计划完成情况", "10", "未建计划记 0 并提示")])}
</tbody></table>
<div class="card-b" style="border-top:1px solid #EEF0F2"><div class="h3">等级分档</div>
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px">
{''.join(f'''<div style="border:1px solid #E4E7EB;border-radius:8px;padding:11px"><div class="tag {t}">{n}</div>
<div class="muted" style="margin-top:7px;line-height:1.7">{d}</div></div>''' for n, d, t in [("已掌握 ≥85", "减少同类题推送", "ok"), ("基本掌握 70-84", "推送 3 道变式题", "info"),
  ("薄弱 50-69", "生成专项练习卷", "warn"), ("严重薄弱 &lt;50", "纳入重点辅导名单", "err")])}</div></div></div>
<div class="card" style="margin:0"><div class="card-h"><h2>规则版本</h2></div><div class="card-b" style="padding:0">
{''.join(f'''<div style="padding:12px 16px;border-bottom:1px solid #F2F4F6;display:flex;justify-content:space-between;align-items:center">
<div><b>{v}</b><div class="muted" style="margin-top:4px">{d} · {p}</div></div>
<span class="tag {'ok' if s == '生效中' else 'gray'}">{s}</span></div>''' for v, d, p, s in [
  ("v3", "2026-10-01 生效", "李静", "生效中"), ("v2", "2026-08-15 生效", "李静", "已归档"),
  ("v1", "2026-03-01 生效", "王振", "已归档")])}
</div><div class="card-b"><div class="h3">规则验证</div>
<div class="muted" style="line-height:2">测试样本 32 条（正常 18 / 边界 8 / 异常 6）<br>相同输入 + v3 规则 → 32/32 结果一致<br>权重合计 100.01 时保存被拒绝（提示差额 0.01）</div>
<button class="btn" style="width:100%;margin-top:12px">运行一致性回归</button></div></div></div>
<div class="card"><div class="card-h"><h2>修正效果看板</h2><span class="sub">用于验证规则是否有效</span></div>
<div class="card-b" style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px">
{''.join(f'''<div><div class="muted">{k}</div><div style="font-size:22px;font-weight:700;color:{C['primary']};margin-top:4px" class="num">{v}</div><div class="muted" style="margin-top:2px">{d}</div></div>''' for k, v, d in [
  ("推荐采纳率", "78.4%", "382 / 487"), ("人工修正率", "7.6%", "37 / 486"),
  ("修正后练习完成率", "82.1%", "较未修正 +14pt"), ("诊断覆盖率", "94.2%", "458 / 486")])}</div></div>""")

# ---------- index ----------
idx = ['<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><title>053 设计稿索引</title>',
       f'<style>body{{font-family:"PingFang SC",sans-serif;background:{C["bg"]};padding:40px;color:{C["text"]}}}',
       f'h1{{font-size:22px}}p{{color:{C["muted"]};margin:10px 0 26px}}',
       '.g{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}a{background:#fff;border:1px solid #E4E7EB;border-radius:10px;padding:16px;display:block}',
       f'a b{{display:block;font-size:13px}}a span{{font-size:11px;color:{C["muted"]}}}</style></head><body>',
       '<h1>高校智能题库与错题本系统 · UI 原型</h1><p>共 18 个页面，覆盖 5 个角色；点击进入可交互 mock</p><div class="g">']
names = {"login": ("登录页", "学生/教师共用"), "dashboard": ("题库统计首页", "管理员·6 图表一屏"),
         "subject": ("学科管理", "教研员"), "knowledge-tree": ("知识点树", "三级树+权重"),
         "question-list": ("题库列表", "分页+多条件"), "question-edit": ("题目编辑", "左录入右预览"),
         "paper-workbench": ("组卷工作台", "三栏组卷"), "paper-list": ("试卷管理", "状态机"),
         "audit": ("题目审核台", "三栏审核"), "import": ("批量导入", "逐行校验"),
         "mastery": ("学情诊断", "教师端·含留痕"), "class-stat": ("班级学情", "排名+热力"),
         "practice-center": ("练习中心", "学生门户"), "answer": ("答题页", "答题卡+计时"),
         "wrong-book": ("我的错题本", "抽屉详情"), "mastery-student": ("我的诊断", "学生端"),
         "user-role": ("用户与角色", "三层权限"), "rule-config": ("规则配置", "权重+版本")}
for k, _ in pages.items():
    n, d = names.get(k, (k, ""))
    idx.append(f'<a href="{k}.html"><b>{n}</b><span>{d}</span></a>')
idx.append("</div></body></html>")
pages["index"] = "".join(idx)

for name, html in pages.items():
    (OUT / f"{name}.html").write_text(html, encoding="utf-8")
print(f"生成 {len(pages)} 个页面")
