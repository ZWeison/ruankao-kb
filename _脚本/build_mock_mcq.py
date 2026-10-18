# -*- coding: utf-8 -*-
"""
生成《综合知识模拟卷（75 题）》—— HTML 交互版 + Markdown 版。

命题依据：本库 _staging 中 2024上、2024下、2025上、2025下 四套
综合知识真题（各 75 题）的题干考点分布，辅以 2026 上半年案例真题
体现的新趋势（架构评估、边缘计算、AIoT、知识图谱、时序数据库、MQTT）。

用法：python _脚本/build_mock_mcq.py
"""
import html as H
import json
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent.parent / "06-模拟考卷"
BASENAME = "综合知识模拟卷-75题-2024至2026高频考点"

GROUPS = [
    ("计算机系统", "一、计算机组成与体系结构"),
    ("操作系统", "二、操作系统"),
    ("数据库", "三、数据库系统"),
    ("计算机网络", "四、计算机网络"),
    ("软件工程", "五、软件工程与开发方法"),
    ("软件测试", "六、软件测试"),
    ("架构设计", "七、软件架构设计"),
    ("信息安全", "八、信息安全"),
    ("新兴技术", "九、新技术与前沿趋势"),
    ("项目管理", "十、项目管理"),
    ("知识产权", "十一、知识产权"),
    ("数学", "十二、应用数学"),
    ("专业英语", "十三、专业英语"),
]

# ---------------------------------------------------------------- 题库
Q = []


def q(tag, freq, stem, opts, ans, exp):
    Q.append(dict(tag=tag, freq=freq, stem=stem, opts=opts, ans=ans, exp=exp))


# ============ 一、计算机系统（7） ============
q("计算机系统", "24上·24下·25上",
  "某计算机的 Cache 命中率为 95%，Cache 存取周期为 2 ns，主存存取周期为 20 ns。采用“先访问 Cache，未命中再访问主存”的串行方式，则平均访问时间约为（ ）。",
  ["2.9 ns", "3.0 ns", "3.9 ns", "11.0 ns"], "B",
  "平均访问时间 = 0.95×2 + 0.05×(2+20) = 1.9 + 1.1 = 3.0 ns。注意未命中时先访问 Cache 的 2 ns 也要计入。")

q("计算机系统", "24下·25上",
  "某总线数据线宽度为 32 位，总线时钟频率为 100 MHz，每个时钟周期传送一次数据，则该总线的数据传输率约为（ ）。",
  ["100 MB/s", "200 MB/s", "400 MB/s", "800 MB/s"], "C",
  "32 位 = 4 B，4 B × 100 M 次/秒 = 400 MB/s（即 3.2 Gb/s）。")

q("计算机系统", "24上·25上",
  "某系统由部件甲与“部件乙、丙并联”两部分串联组成，甲、乙、丙的可靠度均为 0.9，则该系统的可靠度为（ ）。",
  ["0.810", "0.891", "0.900", "0.990"], "B",
  "并联部分可靠度 = 1-(1-0.9)² = 0.99；串联系统 = 0.9 × 0.99 = 0.891。")

q("计算机系统", "24下·25上",
  "某指令流水线分为 5 段，每段耗时 2 ns。在不考虑流水线建立时间的情况下，连续执行 100 条指令所需的时间为（ ）。",
  ["200 ns", "208 ns", "210 ns", "1000 ns"], "B",
  "完成 n 条指令需 (k+n-1)×Δt = (5+100-1)×2 = 208 ns。串行执行则需 100×5×2=1000 ns。")

q("计算机系统", "24下·25上",
  "对 8 位数据进行海明校验，至少需要（ ）位校验位。",
  ["3", "4", "5", "8"], "B",
  "海明码需满足 2^k ≥ n+k+1。k=4 时 16 ≥ 8+4+1=13，成立；k=3 时 8 < 12，不成立。故至少 4 位。")

q("计算机系统", "25上·25下",
  "某系统页大小为 4 KB，物理内存为 8 GB，采用位示图管理空闲页框，则位示图至少占用（ ）。",
  ["128 KB", "256 KB", "512 KB", "1 MB"], "B",
  "页框数 = 8 GB / 4 KB = 2³³ / 2¹² = 2²¹；位示图 2²¹ bit = 2¹⁸ B = 256 KB。")

q("计算机系统", "24下·25上",
  "关于 NOR Flash 与 NAND Flash 的描述，正确的是（ ）。",
  ["NOR Flash 支持随机访问，常用于存放启动代码",
   "NAND Flash 支持字节级随机写，适合存放启动代码",
   "NOR Flash 的单位容量成本低于 NAND Flash",
   "NAND Flash 无需坏块管理，可靠性高于 NOR Flash"], "A",
  "NOR 可字节随机读、支持片内执行（XIP），适合作启动代码；NAND 按页读写、容量大、成本低，但需坏块管理与 ECC，一般作数据存储。")

# ============ 二、操作系统（7） ============
q("操作系统", "24下·25上·25下",
  "一个正在运行的进程因等待 I/O 完成而进入阻塞态。当 I/O 操作完成后，该进程的状态将变为（ ）。",
  ["运行态", "就绪态", "阻塞态", "终止态"], "B",
  "I/O 完成只使进程具备运行条件，还需等待调度，故由阻塞态转为就绪态，不能直接转为运行态。")

q("操作系统", "25下",
  "某临界资源的互斥信号量当前值为 -2，其含义是（ ）。",
  ["有 2 个进程正在同时使用该资源",
   "有 2 个进程在等待进入临界区",
   "该资源还可被 2 个进程使用",
   "有 2 个进程已执行完临界区"], "B",
  "信号量值为负时，绝对值等于等待队列中的进程数；此时有 1 个进程在临界区内、2 个进程在等待。")

q("操作系统", "25上",
  "系统中有 5 个进程，每个进程最多需要 3 个同类资源。为保证系统一定不会发生死锁，该类资源至少需要（ ）个。",
  ["10", "11", "12", "15"], "B",
  "最坏情况是每个进程各持有 2 个（共 10 个）并都在申请第 3 个；再多 1 个资源即可让某进程完成并释放，故至少 5×(3-1)+1 = 11 个。")

q("操作系统", "24上·25上",
  "某单处理机系统采用高响应比优先调度算法。当前有三个作业等待：甲已等待 10 ms、需运行 5 ms；乙已等待 3 ms、需运行 1 ms；丙已等待 8 ms、需运行 4 ms。下一个被调度的作业是（ ）。",
  ["甲", "乙", "丙", "无法确定"], "B",
  "响应比 =（等待时间+要求服务时间）/ 要求服务时间：甲=(10+5)/5=3.0，乙=(3+1)/1=4.0，丙=(8+4)/4=3.0。乙最高，故选乙。")

q("操作系统", "24下·25下",
  "某进程分得 3 个页框，页面访问序列为 1,2,3,4,1,2,5,1,2,3,4,5。采用 LRU 置换算法（初始页框为空），缺页次数为（ ）。",
  ["8", "9", "10", "12"], "C",
  "逐次模拟：前 7 次访问均缺页；随后访问 1、2 命中；访问 3、4、5 各缺页一次。合计 10 次缺页。")

q("操作系统", "25下",
  "某文件系统采用树形目录，当前工作目录为 /usr/local/etc。要访问文件 /usr/bin/tool，使用相对路径应写作（ ）。",
  ["../bin/tool", "../../bin/tool", "/usr/local/bin/tool", "./bin/tool"], "B",
  "从 /usr/local/etc 上跳两级到 /usr，再进入 bin/tool，故相对路径为 ../../bin/tool；以“/”开头的是绝对路径，且题中绝对路径写法本身与目标不符。")

q("操作系统", "25上",
  "三个周期任务 T1、T2、T3 的周期分别为 10 ms、20 ms、50 ms，采用速率单调调度（RMS），优先级从高到低依次为（ ）。",
  ["T1、T2、T3", "T3、T2、T1", "T2、T1、T3", "三者优先级相同"], "A",
  "RMS 按周期分配优先级：周期越短、截止期越紧，优先级越高。故 T1 > T2 > T3。")

# ============ 三、数据库（8） ============
q("数据库", "24下·25上",
  "数据库系统三级模式中，外模式/模式映像的存在保证了数据的（ ）。",
  ["物理独立性", "逻辑独立性", "完整性", "安全性"], "B",
  "外模式/模式映像使模式改变时只需调整映像、不必改应用程序，保证逻辑独立性；模式/内模式映像保证物理独立性。")

q("数据库", "25下",
  "设 R 和 S 是同类关系，则关系表达式 R-(R-S) 等价于（ ）。",
  ["R∪S", "R∩S", "R×S", "S-R"], "B",
  "R-(R-S) = R∩S，这是集合运算的基本恒等式。")

q("数据库", "24下",
  "关系 R(a,b,c) 与 S(b,c,d) 进行自然连接，结果关系的列数为（ ）。",
  ["3", "4", "5", "6"], "B",
  "自然连接在公共属性 b、c 上做等值连接并去掉重复列，结果为 a,b,c,d 共 4 列。")

q("数据库", "24下·25上",
  "关系 R(A,B,C,D)，函数依赖集 F={A→B, B→C, C→D}，则 R 的候选码是（ ）。",
  ["A", "AB", "AC", "AD"], "A",
  "A 的闭包 A⁺ = {A,B,C,D}，且 A 不可再约简，故 A 为候选码；B、C、D 均不能决定全部属性。")

q("数据库", "24下·25上",
  "关系 R(职工号, 职工姓名, 部门号, 部门名称)，其中职工号→职工姓名、职工号→部门号、部门号→部门名称。该关系最高满足（ ）。",
  ["1NF", "2NF", "3NF", "BCNF"], "B",
  "码为职工号，非主属性均完全依赖于码，满足 2NF；但存在职工号→部门号→部门名称的传递依赖，不满足 3NF。")

q("数据库", "24下·25下",
  "事务 T1 修改了某行数据但尚未提交，事务 T2 读取到该行修改后的值，随后 T1 回滚。这种现象称为（ ）。",
  ["脏读", "不可重复读", "幻读", "丢失修改"], "A",
  "读到其他事务未提交且最终回滚的数据即脏读；不可重复读是同一事务内两次读同一行结果不同；幻读是两次查询返回的行数不同。")

q("数据库", "25下",
  "关于两阶段锁协议（2PL），描述正确的是（ ）。",
  ["扩展阶段只能加锁不能解锁，收缩阶段只能解锁不能加锁",
   "事务执行过程中可随时加锁和解锁",
   "只有在收缩阶段才允许加锁",
   "两阶段锁协议可以完全避免死锁"], "A",
  "2PL 分扩展（加锁）与收缩（解锁）两阶段，可保证可串行化，但不能避免死锁（如交叉等待）。")

q("数据库", "25下",
  "数据库设计过程中，将 E-R 图转换为关系模式并进行规范化处理，属于（ ）阶段的工作。",
  ["需求分析", "概念结构设计", "逻辑结构设计", "物理结构设计"], "C",
  "概念设计产出 E-R 图；逻辑设计把 E-R 图转换为关系模式并规范化；物理设计确定存储结构与索引。")

# ============ 四、计算机网络（5） ============
q("计算机网络", "24下·24上",
  "在 OSI 参考模型中，路由器工作于（ ）。",
  ["物理层", "数据链路层", "网络层", "传输层"], "C",
  "路由器依据 IP 地址进行分组转发与路由选择，属网络层设备；二层交换机属数据链路层，中继器/集线器属物理层。")

q("计算机网络", "24下",
  "下列协议中，属于传输层的是（ ）。",
  ["ICMP", "ARP", "UDP", "HTTP"], "C",
  "UDP 与 TCP 同属传输层；ICMP、ARP 属网络层，HTTP 属应用层。")

q("计算机网络", "25下",
  "某子网掩码为 255.255.255.240，则该子网中可分配给主机的地址数量为（ ）。",
  ["6", "14", "16", "30"], "B",
  "240 = 11110000，主机位 4 位，共 2⁴=16 个地址，去掉网络地址与广播地址，可用 14 个。")

q("计算机网络", "24上·25上",
  "某无噪声信道带宽为 4 kHz，采用 16 种不同的信号状态传输数据，则其最大数据传输率约为（ ）。",
  ["8 kbps", "16 kbps", "32 kbps", "64 kbps"], "C",
  "奈奎斯特定理：C = 2W·log₂V = 2×4000×log₂16 = 2×4000×4 = 32 kbps。")

q("计算机网络", "25上",
  "在 RESTful 接口中，对资源进行部分更新应使用的 HTTP 方法是（ ）。",
  ["GET", "PUT", "PATCH", "HEAD"], "C",
  "PUT 用于整体替换资源（幂等），PATCH 用于部分更新，GET 查询，HEAD 只取响应头。")

# ============ 五、软件工程（8） ============
q("软件工程", "24下·25上",
  "某大型软件项目需求不明确、技术风险高，且需要边开发边验证，最适合采用（ ）。",
  ["瀑布模型", "螺旋模型", "V 模型", "净室模型"], "B",
  "螺旋模型以风险分析为核心，每轮迭代都包含风险识别与消解，适合大型、高风险、需求不清的项目。")

q("软件工程", "25上",
  "CMMI 成熟度模型的第 4 级是（ ）。",
  ["已管理级", "已定义级", "量化管理级", "优化级"], "C",
  "五级依次为：初始级、已管理级、已定义级、量化管理级、优化级。")

q("软件工程", "25下",
  "关于 Scrum 的描述，错误的是（ ）。",
  ["产品待办列表由产品负责人维护，并按业务价值排序",
   "Sprint 通常为 2~4 周，期间应保持 Sprint 目标稳定",
   "每日站会用于同步进展、暴露障碍，一般不超过 15 分钟",
   "Sprint 执行期间，产品负责人可随时加入新需求而不影响 Sprint 目标"], "D",
  "Sprint 期间应保护团队不受干扰，新需求进入产品待办列表并留待后续 Sprint 规划，不能随意插入当前 Sprint。")

q("软件工程", "25下·25上",
  "某模块内的处理元素必须按特定次序执行，且前一个元素的输出是后一个元素的输入，该模块的内聚类型是（ ）。",
  ["功能内聚", "顺序内聚", "通信内聚", "逻辑内聚"], "B",
  "顺序内聚强调“有序且数据流串联”；功能内聚是各元素共同完成单一功能；通信内聚是操作同一数据集；逻辑内聚是逻辑相似、可选择执行。")

q("软件工程", "25下",
  "下列耦合类型中，模块间联系最弱（耦合度最低）的是（ ）。",
  ["数据耦合", "标记耦合", "控制耦合", "公共耦合"], "A",
  "耦合由弱到强：非直接 < 数据 < 标记 < 控制 < 外部 < 公共 < 内容。数据耦合只传简单数据参数，联系最弱。")

q("软件工程", "25上·24下",
  "在数据流图中，两个数据流之间用“*”号连接，表示它们之间是（ ）关系。",
  ["或", "与", "异或", "顺序"], "B",
  "数据流图中“*”表示与（同时发生），“+”表示或，“⊕”表示异或（互斥，只能取其一）。")

q("软件工程", "24上·25上",
  "在 UML 用例图中，下列不属于用例之间关系的是（ ）。",
  ["包含（include）", "扩展（extend）", "泛化", "聚合"], "D",
  "用例之间存在包含、扩展与泛化关系；聚合是类之间的关系，用于表达整体与部分。")

q("软件工程", "25下",
  "逆向工程的主要目的是（ ）。",
  ["从已有程序中恢复设计信息", "将设计文档自动转换为源代码",
   "对程序进行性能优化", "替代需求分析阶段的工作"], "A",
  "逆向工程分析程序以恢复设计信息；再工程 = 逆向工程 + 重构 + 前向工程，目的是改善系统而非替代需求分析。")

# ============ 六、软件测试（5） ============
q("软件测试", "25上·24下",
  "下列测试方法中，不属于黑盒测试方法的是（ ）。",
  ["等价类划分", "边界值分析", "因果图法", "基本路径测试"], "D",
  "基本路径测试属于白盒测试；等价类、边界值、因果图、判定表、错误推测均为黑盒方法。")

q("软件测试", "25上·24下",
  "下列白盒测试覆盖准则中，覆盖能力最强的是（ ）。",
  ["语句覆盖", "判定覆盖", "条件组合覆盖", "路径覆盖"], "D",
  "覆盖强度大致为：语句 < 判定 < 条件组合 < 路径。路径覆盖要求执行所有可能路径，最强。")

q("软件测试", "25下",
  "软件测试的标准流程中，正确的顺序是（ ）。",
  ["单元测试→集成测试→系统测试→验收测试",
   "单元测试→系统测试→集成测试→验收测试",
   "集成测试→单元测试→系统测试→验收测试",
   "单元测试→集成测试→验收测试→系统测试"], "A",
  "先验证单元，再验证接口与集成，然后做系统级验证，最后由用户验收。")

q("软件测试", "25上",
  "回归测试的主要目的是（ ）。",
  ["验证修改后的软件未引入新错误，且原有功能仍然正常",
   "发现软件中从未被测试过的缺陷",
   "评估软件的性能是否满足要求",
   "确认软件是否满足用户的全部需求"], "A",
  "回归测试在缺陷修复或变更后执行，重点验证“改动没有破坏原有功能”，通常复用原有用例并补充针对性用例。")

q("软件测试", "25上·25下",
  "关于软件测试与调试，说法错误的是（ ）。",
  ["测试的目的是发现错误，调试的目的是定位并修正错误",
   "测试可以事先设计用例并按计划执行，调试过程难以预先计划",
   "测试通常由独立测试人员完成，调试一般由开发人员完成",
   "调试成功后即可证明程序中不再存在其他错误"], "D",
  "调试成功只说明已发现的错误被修正，不能证明软件无其他错误；测试只能证明缺陷存在，不能证明缺陷不存在。")

# ============ 七、软件架构设计（11） ============
q("架构设计", "24下·25上",
  "在 4+1 视图模型中，关注并发性、同步与性能等需求的视图是（ ）。",
  ["逻辑视图", "进程视图", "开发视图", "物理视图"], "B",
  "逻辑视图对应功能需求；进程视图关注并发、同步与性能；开发视图关注模块与包的组织；物理视图关注软件到硬件的部署。")

q("架构设计", "24上·25上",
  "管道-过滤器风格最适合用于（ ）。",
  ["需要频繁交互的图形界面系统",
   "数据需经过多道独立变换处理的批处理系统",
   "以共享数据为中心的专家系统",
   "对事件进行异步响应的系统"], "B",
  "管道-过滤器把处理分解为独立过滤器，通过数据流管道串联，适合编译、图像处理、数据转换等批处理；缺点是不适合交互式应用。")

q("架构设计", "25上",
  "在黑板体系结构中，控制构件的主要职责是（ ）。",
  ["存储各知识源产生的中间结果",
   "根据黑板当前状态选择并调度知识源执行",
   "负责与外部系统进行数据交换",
   "对最终结果进行一致性校验"], "B",
  "黑板结构由知识源、黑板（共享数据）与控制三部分组成，控制构件依据黑板状态决定激活哪个知识源。")

q("架构设计", "25上",
  "事件驱动（隐式调用）架构风格的主要缺点是（ ）。",
  ["构件之间必须直接引用，耦合度高",
   "系统控制流由事件隐式触发，行为难以预测，调试和测试困难",
   "不支持构件复用",
   "无法支持分布式部署"], "B",
  "隐式调用使构件松耦合、易扩展，但控制流不显式，难以推理整体行为，且不能保证事件处理顺序。")

q("架构设计", "25下",
  "解释器体系结构通常由四部分组成，即解释引擎、被解释程序的存储区、（ ）以及记录解释执行进度的数据结构。",
  ["解释器的内部状态", "数据库服务器", "事件总线", "规则库"], "A",
  "解释器四要素：解释引擎、被解释代码、解释器内部状态（当前工作状态）、记录执行进度的数据结构。")

q("架构设计", "24下",
  "在进程通信体系结构风格中，构件之间的连接件是（ ）。",
  ["数据流管道", "消息传递机制", "函数调用", "共享黑板"], "B",
  "进程通信风格以独立进程为构件，通过显式的消息传递（同步或异步）协作；管道是管道-过滤器风格的连接件。")

q("架构设计", "24下",
  "基于架构的软件开发方法（ABSD）中，体系结构需求主要来源于（ ）。",
  ["系统的质量目标、系统的商业目标、系统开发人员的商业目标",
   "用户需求、市场需求、竞争对手需求",
   "功能需求、非功能需求、约束条件",
   "领域模型、用例模型、数据模型"], "A",
  "ABSD 把体系结构需求归结为三类驱动因素：系统的质量目标、系统的商业目标、系统开发人员的商业目标。")

q("架构设计", "24下·25下",
  "按教材划分，下列不属于特定领域软件体系结构（DSSA）参与角色的是（ ）。",
  ["领域专家", "领域分析师", "领域设计人员", "最终用户"], "D",
  "DSSA 的四类角色为领域专家、领域分析师、领域设计人员、领域实现人员；最终用户不是其定义的角色。")

q("架构设计", "24下·25下",
  "使用效用树对质量属性场景排序时，采用的两个维度是（ ）。",
  ["场景对系统成功的重要性、实现该场景的技术难度",
   "场景的发生概率、场景的影响范围",
   "开发成本、开发周期",
   "用户满意度、系统吞吐量"], "A",
  "效用树按“业务重要性（对系统成功的重要性）”和“技术难度（实现难度）”两个维度给场景打 (H/M/L)，据此确定架构关注点优先级。")

q("架构设计", "25下",
  "在架构评估中，将加密强度由 128 位提高到 256 位会提升安全性但增加处理时间。该决策点属于（ ）。",
  ["敏感点", "权衡点", "风险点", "非风险点"], "B",
  "该决策同时影响安全性（正）与性能（负），是多质量属性之间的折中，故为权衡点；敏感点是影响单一质量属性的关键决策。")

q("架构设计", "25上",
  "微服务架构中，断路器（Circuit Breaker）的三种状态是（ ）。",
  ["关闭、打开、半开", "启动、运行、停止", "正常、降级、熔断", "空闲、忙、阻塞"], "A",
  "Closed 正常放行并统计失败率；失败率超阈值转 Open 直接拒绝；超时后进入 Half-Open 放行少量请求探测，成功则 Closed，失败则重新 Open。")

# ============ 八、信息安全（5） ============
q("信息安全", "24上·24下",
  "信息安全的基本要素不包括（ ）。",
  ["机密性", "完整性", "可用性", "可移植性"], "D",
  "信息安全五要素为机密性、完整性、可用性、可控性、不可否认性；可移植性是软件质量属性。")

q("信息安全", "25下",
  "关于数字签名的描述，正确的是（ ）。",
  ["用发送方私钥签名，接收方用发送方公钥验证",
   "用接收方公钥签名，接收方用私钥验证",
   "签名同时保证了报文的机密性",
   "签名只能用于身份认证，不能保证数据完整性"], "A",
  "数字签名用发送方私钥对报文摘要签名，接收方用其公钥验证，可保证完整性、身份真实性与不可否认性，但不提供机密性。")

q("信息安全", "25下",
  "下列不属于 PKI 组成部分的是（ ）。",
  ["认证机构 CA", "注册机构 RA", "证书撤销列表 CRL", "入侵检测系统 IDS"], "D",
  "PKI 由 CA、RA、证书库、证书撤销（CRL/OCSP）、密钥备份与恢复、应用接口等组成；IDS 属于安全防护设备，不是 PKI 组件。")

q("信息安全", "24下",
  "防范 SQL 注入最有效的措施是（ ）。",
  ["对用户输入中的单引号进行转义后拼接 SQL",
   "使用参数化查询（预编译语句）",
   "限制输入长度不超过 20 个字符",
   "将数据库端口改为非默认端口"], "B",
  "参数化查询让输入始终作为数据而非 SQL 语法的一部分，从根源上消除注入；转义易被绕过，长度限制与改端口只是辅助。")

q("信息安全", "24上",
  "依据《计算机信息系统安全保护等级划分准则》，计算机信息系统安全保护等级的最高级是（ ）。",
  ["系统审计保护级", "安全标记保护级", "结构化保护级", "访问验证保护级"], "D",
  "五级依次为：用户自主保护级、系统审计保护级、安全标记保护级、结构化保护级、访问验证保护级。")

# ============ 九、新兴技术（7） ============
q("新兴技术", "24上·26上",
  "物联网应用通常分为三层，自下而上依次是（ ）。",
  ["感知层、网络层、应用层", "物理层、链路层、应用层",
   "设备层、平台层、服务层", "感知层、传输层、会话层"], "A",
  "物联网经典三层为感知层（采集与识别）、网络层（传输）、应用层（业务处理与服务）。")

q("新兴技术", "25上·26上",
  "下列不属于边缘计算优势的是（ ）。",
  ["减少数据上传，降低带宽与云端存储成本",
   "就近处理，降低端到端时延",
   "网络中断时仍可在本地提供部分服务",
   "设备与算力高度集中，便于统一运维和集中升级"], "D",
  "边缘计算的特点是节点分散、异构，运维与升级反而更复杂；集中运维是云计算/集中式资源池的优势。")

q("新兴技术", "24上",
  "数字孪生的核心特征是（ ）。",
  ["物理实体与虚拟模型之间的实时映射与双向交互",
   "对海量数据进行离线批处理分析",
   "用区块链保证数据的不可篡改",
   "将计算任务全部迁移到云端执行"], "A",
  "数字孪生通过数据采集与模型仿真，实现物理实体的虚拟映射、实时同步与双向交互，典型能力包括描述、诊断、预测与决策。")

q("新兴技术", "25上·26上",
  "区块链中智能合约的主要作用是（ ）。",
  ["在满足预设条件时自动执行约定的业务规则，且执行结果不可篡改",
   "对链上数据进行压缩存储",
   "为节点提供共识算法",
   "负责生成公私钥对"], "A",
  "智能合约是部署在链上的可编程规则，条件触发即自动执行，结果经共识确认后不可篡改，用于减少人工干预与信任成本。")

q("新兴技术", "25上·26上",
  "构建知识图谱的合理步骤是（ ）。",
  ["知识抽取→知识融合→知识加工",
   "知识融合→知识抽取→知识加工",
   "知识加工→知识抽取→知识融合",
   "知识抽取→知识加工→知识融合"], "A",
  "先从多源数据抽取实体、关系与属性，再消解冲突与冗余完成融合，最后做表示、存储、推理与质量验证（加工）。")

q("新兴技术", "25上·25下",
  "当前大语言模型普遍采用的 Transformer 架构，其核心机制是（ ）。",
  ["卷积", "循环门控", "自注意力", "决策树"], "C",
  "Transformer 以多头自注意力替代循环结构，可并行建模长距离依赖，是 GPT 等大模型的基础。")

q("新兴技术", "25下",
  "云原生“不可变基础设施”的核心含义是（ ）。",
  ["服务器一旦部署就不再修改，所有变更通过构建新实例并替换旧实例完成",
   "基础设施的配置文件不允许纳入版本控制",
   "虚拟机磁盘必须设置为只读",
   "容器镜像一旦构建就不能被打标签"], "A",
  "不可变基础设施要求实例部署后不做原地修改，变更通过新镜像/新实例替换实现，从而保证环境一致、可回滚、可重复。")

# ============ 十、项目管理（3） ============
q("项目管理", "24上·24下·25上",
  "某项目活动及依赖关系如下：A(3 天)、B(4 天) 无紧前活动；C(2 天) 紧前为 A；D(5 天) 紧前为 A、B；E(3 天) 紧前为 C、D；F(2 天) 紧前为 D；G(4 天) 紧前为 E、F。该项目的最短工期为（ ）。",
  ["14 天", "15 天", "16 天", "17 天"], "C",
  "关键路径为 B→D→E→G：4+5+3+4=16 天；其余路径 A-C-E-G=12、A-D-E-G=15、A-D-F-G=14、B-D-F-G=15，均不超过 16 天。")

q("项目管理", "24下·25上",
  "某项目当前 PV=100 万元，EV=80 万元，AC=90 万元，则项目状态是（ ）。",
  ["进度提前、成本节约", "进度落后、成本超支", "进度落后、成本节约", "进度提前、成本超支"], "B",
  "SPI=EV/PV=0.8<1，进度落后；CPI=EV/AC≈0.89<1，成本超支。")

q("项目管理", "24下",
  "下列活动中，不属于软件配置管理范畴的是（ ）。",
  ["配置项标识", "版本控制", "变更控制", "性能测试"], "D",
  "配置管理包括配置标识、版本控制、变更控制、配置审计与状态报告；性能测试属于测试活动。")

# ============ 十一、知识产权（2） ============
q("知识产权", "25上",
  "关于软件著作权的取得，说法正确的是（ ）。",
  ["软件著作权自软件开发完成之日起自动产生，登记不是取得权利的前提",
   "软件必须经登记后才能取得著作权",
   "软件著作权自首次发表之日起产生",
   "软件著作权需每年续展一次"], "A",
  "我国著作权采用自动保护原则，作品完成即产生权利；软件登记是自愿的，仅作为权利证明，便于维权。")

q("知识产权", "25下",
  "依据我国专利法，发明专利权的保护期限为（ ）。",
  ["10 年", "15 年", "20 年", "50 年"], "C",
  "发明专利权 20 年、实用新型专利权 10 年、外观设计专利权 15 年，均自申请日起计算。")

# ============ 十二、应用数学（2） ============
q("数学", "24下·25上·25下",
  "某单位 100 名员工中，会 Java 的 45 人，会 Python 的 53 人，会 C++ 的 55 人；既会 Java 又会 Python 的 28 人，既会 Python 又会 C++ 的 35 人，既会 Java 又会 C++ 的 32 人，三种都会的 20 人。则三种语言都不会的人数为（ ）。",
  ["18", "20", "22", "24"], "C",
  "容斥原理：至少会一种 = 45+53+55-28-35-32+20 = 78；故都不会 = 100-78 = 22 人。")

q("数学", "25上",
  "已知约束条件 x≥1，y≥x，x+y≤6，则 y/x 的最大值是（ ）。",
  ["3", "4", "5", "6"], "C",
  "可行域中 y≤6-x，故 y/x ≤ (6-x)/x = 6/x-1，在 x=1 时取最大 5（此时 y=5）。")

# ============ 十三、专业英语（5） ============
PASSAGE = """Event-driven architecture (EDA) is a design paradigm in which the flow of a system is determined by events—significant changes in state that are produced, detected or consumed by loosely coupled components. Instead of invoking one another directly, services communicate through an event (1) ______ that decouples producers from consumers. A producer publishes an event without knowing which components, if any, will react to it, and consumers subscribe to the event types they care about. This indirection improves (2) ______ , because new consumers can be added without modifying producers; however, it also makes the overall behaviour harder to reason about and to (3) ______ . Since delivery is usually asynchronous, an EDA must cope with duplicated or out-of-order messages, which is why consumers are expected to be (4) ______ . Two common topologies are the broker topology, in which a central broker routes events without a central coordinator, and the mediator topology, in which a mediator (5) ______ the steps of a complex process and can trigger compensation when a step fails."""

q("专业英语", "25下",
  "空 (1) 应填入（ ）。",
  ["gateway", "broker", "repository", "sandbox"], "B",
  "event broker（事件代理）负责接收与转发事件，使生产者与消费者解耦。")

q("专业英语", "25下",
  "空 (2) 应填入（ ）。",
  ["cohesion", "redundancy", "latency", "scalability"], "D",
  "新增消费者无需修改生产者，提升的是可扩展性（scalability）。cohesion 是内聚，redundancy 是冗余。")

q("专业英语", "25下",
  "空 (3) 应填入（ ）。",
  ["debug", "deploy", "encrypt", "compress"], "A",
  "与“harder to reason about”并列，指系统行为更难推理与调试（debug）。")

q("专业英语", "25下",
  "空 (4) 应填入（ ）。",
  ["stateless", "atomic", "idempotent", "synchronous"], "C",
  "消息可能重复投递，因此消费者应具备幂等性（idempotent），重复处理不产生额外副作用。")

q("专业英语", "25下",
  "空 (5) 应填入（ ）。",
  ["orchestrates", "audits", "caches", "batches"], "A",
  "mediator 负责编排（orchestrate）复杂流程的各步骤，并在失败时触发补偿。")

assert len(Q) == 75, len(Q)

# 均衡答案分布：按 A/B/C/D 循环轮转选项，避免答案过度集中在某一项
_TARGET = ("ABCD" * 19)[:75]
for _i, _item in enumerate(Q):
    _cur = "ABCD".index(_item["ans"])
    _tgt = "ABCD".index(_TARGET[_i])
    _k = (_tgt - _cur) % 4
    if _k:
        _item["opts"] = _item["opts"][-_k:] + _item["opts"][:-_k]
        _item["ans"] = "ABCD"[_tgt]


from collections import Counter
TAG_COUNT = Counter(x["tag"] for x in Q)
GROUP_TITLE = dict(GROUPS)

# ---------------------------------------------------------------- 生成 HTML
CSS = """
:root{
  --page-w:1080px; --ff-head:"PingFang SC","Microsoft YaHei","黑体",SimHei,sans-serif;
  --ff-body:"Songti SC","Microsoft YaHei",SimSun,serif; --ff-mono:"JetBrains Mono",Consolas,monospace;
  --c-primary:#2563EB; --c-text:#111827; --c-muted:#6B7280; --c-border:#E5E7EB;
  --c-bg:#fff; --c-soft:#EEF2FF; --c-code:#F9FAFB; --c-ok:#047857; --c-ok-bg:#ECFDF5;
}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:var(--ff-body);font-size:16px;line-height:1.8;color:var(--c-text);
  background:#F3F4F6;padding:26px 20px 80px}
.wrap{max-width:var(--page-w);margin:0 auto;background:var(--c-bg);padding:44px 52px 60px;
  border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,.08),0 8px 32px rgba(0,0,0,.06)}
h1,h2,h3,h4{font-family:var(--ff-head);line-height:1.35;font-weight:700}
.cover{text-align:center;padding:10px 0 26px;border-bottom:1px solid var(--c-border);margin-bottom:22px}
.eyebrow{font-family:var(--ff-head);font-size:12px;letter-spacing:.18em;color:var(--c-primary);margin-bottom:14px}
.cover h1{font-size:26px;margin-bottom:10px}
.cover .sub{font-size:13.5px;color:var(--c-muted);margin-bottom:18px}
.cover .info{font-size:13px;line-height:2}
.cover .info b{color:var(--c-primary)}
.cover .date{font-size:12px;color:var(--c-muted);margin-top:14px}
.toolbar{position:sticky;top:0;z-index:60;display:flex;flex-wrap:wrap;gap:8px;align-items:center;
  background:rgba(255,255,255,.96);backdrop-filter:blur(6px);border:1px solid var(--c-border);
  border-radius:8px;padding:10px 12px;margin-bottom:18px}
.btn{font-family:var(--ff-head);font-size:12.5px;padding:6px 13px;border-radius:6px;
  border:1px solid var(--c-border);background:#fff;color:var(--c-text);cursor:pointer;white-space:nowrap}
.btn:hover{border-color:var(--c-primary);color:var(--c-primary)}
.btn.primary{background:var(--c-primary);border-color:var(--c-primary);color:#fff}
.btn.primary:hover{opacity:.9;color:#fff}
.btn.ok{background:var(--c-ok);border-color:var(--c-ok);color:#fff}
.btn.danger:hover{border-color:#DC2626;color:#DC2626}
.timer{font-family:var(--ff-mono);font-size:14px;font-weight:600;padding:5px 11px;border-radius:6px;
  background:var(--c-soft);color:var(--c-primary);min-width:82px;text-align:center}
.timer.warn{background:#FEF2F2;color:#DC2626}
.spacer{flex:1}
.progress{font-family:var(--ff-head);font-size:12.5px;color:var(--c-muted)}
.cardbox{background:var(--c-code);border:1px solid var(--c-border);border-radius:8px;padding:14px 16px;margin-bottom:8px}
.cardbox .t{font-family:var(--ff-head);font-size:12.5px;font-weight:700;color:var(--c-muted);margin-bottom:10px;letter-spacing:.06em}
.card{display:grid;grid-template-columns:repeat(15,1fr);gap:6px}
.card a{display:block;text-align:center;font-family:var(--ff-mono);font-size:12px;padding:4px 0;
  border:1px solid var(--c-border);border-radius:4px;color:var(--c-muted);text-decoration:none;background:#fff}
.card a:hover{border-color:var(--c-primary);color:var(--c-primary)}
.card a.done{background:var(--c-soft);border-color:#C7D2FE;color:var(--c-primary)}
.card a.ok{background:var(--c-ok-bg);border-color:#6EE7B7;color:var(--c-ok)}
.card a.bad{background:#FEF2F2;border-color:#FCA5A5;color:#DC2626}
h2{font-size:17px;margin:34px 0 6px;padding:8px 12px;background:var(--c-soft);
  border-left:4px solid var(--c-primary);border-radius:0 6px 6px 0}
.qitem{padding:16px 0 10px;border-bottom:1px dashed var(--c-border)}
.qhead{display:flex;gap:8px;align-items:baseline;flex-wrap:wrap;margin-bottom:8px}
.qno{font-family:var(--ff-head);font-weight:700;font-size:15px;color:var(--c-primary)}
.tag{font-family:var(--ff-head);font-size:10.5px;padding:1px 7px;border-radius:4px;
  background:#F3F4F6;color:var(--c-muted)}
.tag.freq{background:#FFFBEB;color:#B45309}
.stem{font-size:15px;margin-bottom:4px}
.opt{display:flex;gap:9px;align-items:flex-start;border:1px solid var(--c-border);border-radius:6px;
  padding:7px 11px;margin:7px 0;cursor:pointer;font-size:14.5px;transition:.12s}
.opt:hover{background:#F8FAFF;border-color:#C7D2FE}
.opt input{margin-top:6px;flex:0 0 auto}
.opt .lt{font-family:var(--ff-head);font-weight:700;color:var(--c-muted);flex:0 0 auto}
.opt.correct{background:var(--c-ok-bg);border-color:#6EE7B7}
.opt.correct .lt{color:var(--c-ok)}
.opt.wrong{background:#FEF2F2;border-color:#FCA5A5}
.opt.wrong .lt{color:#DC2626}
.expl{display:none;font-size:13.5px;background:var(--c-code);border-left:3px solid #A7F3D0;
  padding:9px 13px;margin:9px 0 2px;border-radius:0 6px 6px 0;color:#374151}
.expl.show{display:block}
.expl b{color:var(--c-ok)}
#result{display:none;margin:24px 0;border:1px solid #A7F3D0;background:var(--c-ok-bg);
  border-radius:8px;padding:18px 20px}
#result.show{display:block}
#result .big{font-family:var(--ff-head);font-size:26px;font-weight:700;color:var(--c-ok)}
#result table{width:100%;border-collapse:collapse;margin-top:12px;font-size:13px}
#result th,#result td{border:1px solid #A7F3D0;padding:6px 9px;background:#fff}
#result th{background:#D1FAE5;font-family:var(--ff-head)}
.passage{background:#FCFCFD;border:1px solid var(--c-border);border-radius:6px;
  padding:14px 16px;margin:14px 0;font-size:14px;line-height:1.9}
.passage p{margin:6px 0}
.note{background:var(--c-code);border-left:3px solid var(--c-border);padding:10px 14px;
  margin:12px 0;font-size:13.5px}
table.dist{width:100%;border-collapse:collapse;margin:12px 0;font-size:13px}
table.dist th,table.dist td{border:1px solid var(--c-border);padding:6px 9px;text-align:left}
table.dist th{background:var(--c-code);font-family:var(--ff-head)}
.foot{margin-top:36px;border-top:1px solid var(--c-border);padding-top:14px;font-size:12.5px;color:var(--c-muted)}
.toast{position:fixed;left:50%;bottom:28px;transform:translate(-50%,20px);background:#111827;color:#fff;
  font-family:var(--ff-head);font-size:13px;padding:10px 20px;border-radius:8px;opacity:0;
  pointer-events:none;transition:.25s;z-index:999}
.toast.show{opacity:1;transform:translate(-50%,0)}
@media (max-width:1160px){.wrap{padding:36px 30px 50px}}
@media (max-width:860px){.wrap{padding:26px 18px 40px}.card{grid-template-columns:repeat(10,1fr)}}
@media (max-width:600px){body{padding:10px 6px 50px}.card{grid-template-columns:repeat(6,1fr)}
  .cover h1{font-size:21px}.opt{font-size:14px}}
@media print{
  body{background:#fff;padding:0}
  .wrap{box-shadow:none;padding:0;max-width:none}
  .toolbar,.cardbox,.toast{display:none!important}
  .expl{display:block!important}
  .qitem{break-inside:avoid}
}
"""


def opts_html(i, item):
    out = []
    for idx, text in enumerate(item["opts"]):
        letter = "ABCD"[idx]
        out.append(
            f'<label class="opt" data-opt="{letter}">'
            f'<input type="radio" name="q{i}" value="{letter}">'
            f'<span class="lt">{letter}</span><span>{H.escape(text)}</span></label>'
        )
    return "\n".join(out)


body_parts = []
for i, item in enumerate(Q, start=1):
    if i == 1 or Q[i - 2]["tag"] != item["tag"]:
        body_parts.append(f'<h2 id="g-{item["tag"]}">{GROUP_TITLE[item["tag"]]}（{TAG_COUNT[item["tag"]]} 题）</h2>')
    if i == 71:
        body_parts.append(f'<div class="passage"><p><b>【阅读材料】</b></p><p>{H.escape(PASSAGE)}</p></div>')
    body_parts.append(f'''<div class="qitem" id="q{i}" data-tag="{item["tag"]}" data-ans="{item["ans"]}">
  <div class="qhead"><span class="qno">{i}.</span>
    <span class="tag">{item["tag"]}</span><span class="tag freq">同类考点：{item["freq"]}</span></div>
  <div class="stem">{H.escape(item["stem"])}</div>
  <div class="opts">
{opts_html(i, item)}
  </div>
  <div class="expl"><b>答案：{item["ans"]}</b>　{item["exp"]}</div>
</div>''')

group_rows = "".join(
    f'<tr><td>{GROUP_TITLE[t]}</td><td>{n}</td><td>{n}</td></tr>'
    for t, n in [(g[0], TAG_COUNT[g[0]]) for g in GROUPS]
)

HTML_DOC = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>系统架构设计师 · 综合知识模拟卷（75 题）</title>
<style>__CSS__</style>
</head>
<body>
<div class="wrap">
<header class="cover">
  <div class="eyebrow">软考 · 系统架构设计师 · 综合知识 · 模拟卷</div>
  <h1>综合知识模拟试卷（75 题）<br>2024 — 2026 高频考点</h1>
  <div class="sub">计算机系统 · 操作系统 · 数据库 · 网络 · 软件工程 · 测试 · 架构设计 · 安全 · 新技术 · 项目管理 · 知识产权 · 数学 · 专业英语</div>
  <div class="info">题量：<b>75 题单选</b>　｜　满分：<b>75 分</b>（每题 1 分）　｜　建议用时：<b>150 分钟</b><br>
  <span style="font-size:12.5px;color:#6B7280">实战：机考 150 分钟，75 题，60 分及格</span></div>
  <div class="date">2026 年 10 月　·　依据本库 2024上/2024下/2025上/2025下 四套综合知识真题考点自主命制　·　非真题</div>
</header>

<div class="toolbar">
  <span class="timer" id="timer">150:00</span>
  <button class="btn primary" id="btnTimer">开始计时</button>
  <button class="btn" id="btnResetTimer">重置计时</button>
  <button class="btn ok" id="btnGrade">交卷判分</button>
  <button class="btn" id="btnToggleExp">显示全部解析</button>
  <span class="spacer"></span>
  <span class="progress" id="progress">已答 0/75</span>
  <button class="btn danger" id="btnClear">清空重做</button>
  <button class="btn" id="btnPrint">打印 / 导出 PDF</button>
</div>

<div class="cardbox">
  <div class="t">答 题 卡（点击题号跳转）</div>
  <div class="card">__CARD__</div>
</div>

<div id="result"></div>

__BODY__

<div class="foot">
  <p><b>命题说明：</b>本卷按四套综合知识真题的板块配额命制，题号顺序与真题一致（1~75），题干与选项全部重新编写，<b>不是真题</b>；参考答案按教材与考点整理，非官方评分标准。</p>
  <p style="margin-top:8px"><b>板块题量：</b>__DIST__</p>
  <p style="margin-top:8px"><b>做题建议：</b>① 先做会的，超过 2 分钟无思路的先标记跳过；② 计算题（Cache、流水线、可靠性、子网、信道容量、关键路径、容斥）务必动笔；③ 交卷后按板块正确率定位薄弱环节，再回到 <code>05-案例专题/</code> 补强。</p>
</div>
</div>
<div class="toast" id="toast"></div>
<script>
(function(){
  "use strict";
  var STORE = "ruankao_mock_mcq_2026";
  var TOTAL = 75;
  var state = { answers:{}, seconds:150*60, running:false, graded:false };

  function load(){
    try{ var raw=localStorage.getItem(STORE); if(raw){ var o=JSON.parse(raw); state.answers=o.answers||{}; } }catch(e){}
  }
  function save(){ try{ localStorage.setItem(STORE, JSON.stringify({answers:state.answers})); }catch(e){} }

  var items = [].slice.call(document.querySelectorAll(".qitem"));
  var timerEl=document.getElementById("timer"), progEl=document.getElementById("progress");
  var toastEl=document.getElementById("toast"), tTimer=null;
  function toast(m){ toastEl.textContent=m; toastEl.classList.add("show");
    clearTimeout(tTimer); tTimer=setTimeout(function(){toastEl.classList.remove("show");},1600); }

  function updateProgress(){
    var n=0;
    items.forEach(function(it){ var id=it.id.slice(1);
      if(document.querySelector('input[name="q'+id+'"]:checked')) n++; });
    progEl.textContent="已答 "+n+"/"+TOTAL;
  }
  function paintCard(){
    items.forEach(function(it){ var id=it.id.slice(1);
      var a=document.querySelector('.card a[href="#q'+id+'"]'); if(!a) return;
      var chosen=document.querySelector('input[name="q'+id+'"]:checked');
      a.className = chosen ? "done" : "";
    });
  }

  items.forEach(function(it){
    var id=it.id.slice(1);
    var ins=[].slice.call(it.querySelectorAll('input[type=radio]'));
    ins.forEach(function(inp){
      if(state.answers[id]===inp.value) inp.checked=true;
      inp.addEventListener("change",function(){
        state.answers[id]=inp.value; save(); updateProgress(); if(!state.graded) paintCard();
      });
    });
  });

  document.getElementById("btnGrade").addEventListener("click",function(){
    var correct=0, blank=0, stats={};
    items.forEach(function(it){
      var id=it.id.slice(1), tag=it.dataset.tag, ans=it.dataset.ans;
      stats[tag]=stats[tag]||{n:0,ok:0};
      stats[tag].n++;
      var chosen=document.querySelector('input[name="q'+id+'"]:checked');
      var labels=[].slice.call(it.querySelectorAll(".opt"));
      labels.forEach(function(l){
        l.classList.remove("correct","wrong");
        if(l.dataset.opt===ans) l.classList.add("correct");
        if(chosen && l.dataset.opt===chosen.value && chosen.value!==ans) l.classList.add("wrong");
      });
      it.querySelector(".expl").classList.add("show");
      var a=document.querySelector('.card a[href="#q'+id+'"]');
      if(!chosen){ blank++; if(a) a.className="bad"; }
      else if(chosen.value===ans){ correct++; stats[tag].ok++; if(a) a.className="ok"; }
      else { if(a) a.className="bad"; }
    });
    state.graded=true;
    var score=correct;
    var rows="";
    Object.keys(stats).forEach(function(t){
      var s=stats[t]; if(s.n===0) return;
      var rate=Math.round(s.ok/s.n*100);
      var color = rate>=80?"#047857":(rate>=60?"#B45309":"#DC2626");
      rows+='<tr><td>'+t+'</td><td>'+s.n+'</td><td>'+s.ok+'</td><td style="color:'+color+';font-weight:700">'+rate+'%</td></tr>';
    });
    var lvl = score>=60?"及格（≥60 分）":(score>=45?"接近及格，重点补短板":"需系统复习");
    var r=document.getElementById("result");
    r.innerHTML='<div class="big">'+score+' / 75 分</div><div style="margin-top:4px;font-size:14px">'
      +'正确 '+correct+' 题　·　错误 '+(75-blank-correct)+' 题　·　未答 '+blank+' 题　·　'+lvl+'</div>'
      +'<table><tr><th>板块</th><th>题数</th><th>正确</th><th>正确率</th></tr>'+rows+'</table>'
      +'<div style="margin-top:10px;font-size:13px;color:#065F46">解析已全部展开；答错的题目标题下方选项标红，正确选项标绿。</div>';
    r.classList.add("show");
    r.scrollIntoView({behavior:"smooth",block:"start"});
    toast("已交卷："+score+" 分");
  });

  var expAll=false;
  document.getElementById("btnToggleExp").addEventListener("click",function(){
    expAll=!expAll;
    document.querySelectorAll(".expl").forEach(function(e){ e.classList.toggle("show",expAll); });
    this.textContent=expAll?"隐藏全部解析":"显示全部解析";
  });

  document.getElementById("btnClear").addEventListener("click",function(){
    if(!confirm("确定清空全部作答并重新开始？")) return;
    state.answers={}; state.graded=false; localStorage.removeItem(STORE);
    document.querySelectorAll('input[type=radio]').forEach(function(i){i.checked=false;});
    document.querySelectorAll(".opt").forEach(function(l){l.classList.remove("correct","wrong");});
    document.querySelectorAll(".expl").forEach(function(e){e.classList.remove("show");});
    document.querySelectorAll(".card a").forEach(function(a){a.className="";});
    document.getElementById("result").classList.remove("show");
    updateProgress(); toast("已清空");
  });

  document.getElementById("btnPrint").addEventListener("click",function(){
    document.querySelectorAll(".expl").forEach(function(e){e.classList.add("show");});
    setTimeout(function(){window.print();},120);
  });

  function fmt(s){ s=Math.max(0,s); var m=Math.floor(s/60), ss=s%60;
    return (m<10?"0":"")+m+":"+(ss<10?"0":"")+ss; }
  function render(){ timerEl.textContent=fmt(state.seconds); timerEl.classList.toggle("warn",state.seconds<=600); }
  var tick=null, btnT=document.getElementById("btnTimer");
  btnT.addEventListener("click",function(){
    state.running=!state.running;
    if(state.running){
      btnT.textContent="暂停计时";
      tick=setInterval(function(){ state.seconds--; render();
        if(state.seconds<=0){ clearInterval(tick); state.running=false; btnT.textContent="开始计时"; toast("时间到！"); }
      },1000);
      toast("计时开始，建议 150 分钟");
    }else{ clearInterval(tick); btnT.textContent="继续计时"; }
  });
  document.getElementById("btnResetTimer").addEventListener("click",function(){
    clearInterval(tick); state.running=false; state.seconds=150*60; btnT.textContent="开始计时"; render();
  });

  load();
  items.forEach(function(it){ var id=it.id.slice(1);
    var v=state.answers[id];
    if(v){ var inp=document.querySelector('input[name="q'+id+'"][value="'+v+'"]'); if(inp) inp.checked=true; }
  });
  render(); updateProgress(); paintCard();
  document.addEventListener("keydown",function(e){
    if((e.ctrlKey||e.metaKey)&&e.key==="s"){ e.preventDefault(); save(); toast("已保存到本地"); }
  });
})();
</script>
</body>
</html>
"""

card = "".join(f'<a href="#q{i}">{i}</a>' for i in range(1, 76))
dist = "　".join(f"{GROUP_TITLE[g[0]]} {TAG_COUNT[g[0]]}" for g in GROUPS)

html_out = (HTML_DOC
            .replace("__CSS__", CSS)
            .replace("__CARD__", card)
            .replace("__BODY__", "\n".join(body_parts))
            .replace("__DIST__", dist))

# ---------------------------------------------------------------- 生成 Markdown
md = []
md.append("---")
md.append("文档类型: 模拟考卷")
md.append("科目: 综合知识")
md.append("题量: 75")
md.append("满分: 75")
md.append("题目类型: 选择题")
md.append("来源类型: 模拟题")
md.append("是否官方: false")
md.append("含答案: true")
md.append("考点标签: [计算机系统, 操作系统, 数据库, 计算机网络, 软件工程, 软件测试, 架构设计, 信息安全, 新兴技术, 项目管理, 知识产权]")
md.append("校对状态: 草稿")
md.append("命制日期: 2026-10-18")
md.append("命题依据: 本库 _staging/imported/01-真题-按年份 下 2024上、2024下、2025上、2025下 四套综合知识真题")
md.append("---")
md.append("")
md.append("# 系统架构设计师 · 综合知识模拟卷（75 题）")
md.append("")
md.append("> **本卷不是真题**。题干、选项、场景均为重新编写，依据本库四套 2024—2025 综合知识真题的**板块配额与考点分布**命制，"
          "并结合 2026 上半年案例真题体现的新趋势（架构评估、边缘计算、AIoT、知识图谱、时序数据库、MQTT）补足新技术题。")
md.append(">")
md.append("> - 题量 **75 题单选**，每题 1 分，满分 **75 分**，建议 **150 分钟**")
md.append("> - 实战 60 分及格；做完在 HTML 版交卷可自动按板块统计正确率")
md.append("")
md.append("## 板块配额")
md.append("")
md.append("| 板块 | 题号 | 题量 |")
md.append("|---|---|:---:|")
start = 1
for tag, title in GROUPS:
    n = TAG_COUNT[tag]
    md.append(f"| {title} | {start}~{start+n-1} | {n} |")
    start += n
md.append("")
md.append("## 试题")
md.append("")

idx = 0
for tag, title in GROUPS:
    md.append(f"### {title}（{TAG_COUNT[tag]} 题）")
    md.append("")
    while idx < len(Q) and Q[idx]["tag"] == tag:
        item = Q[idx]
        no = idx + 1
        if no == 71:
            md.append("**阅读材料**")
            md.append("")
            md.append(PASSAGE)
            md.append("")
        md.append(f"**{no}.** {item['stem']}")
        md.append("")
        for j, o in enumerate(item["opts"]):
            md.append(f"- {'ABCD'[j]}. {o}")
        md.append("")
        idx += 1

md.append("---")
md.append("")
md.append("## 答案速查")
md.append("")
md.append("| 题号 | 答案 | 题号 | 答案 | 题号 | 答案 | 题号 | 答案 | 题号 | 答案 |")
md.append("|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|")
for r in range(15):
    cells = []
    for c in range(5):
        n = r + 1 + c * 15
        cells += [str(n), f"**{Q[n-1]['ans']}**"]
    md.append("| " + " | ".join(cells) + " |")
md.append("")
md.append("## 解析")
md.append("")
for i, item in enumerate(Q, start=1):
    md.append(f"**{i}. 答案 {item['ans']}**　〔{item['tag']}〕")
    md.append("")
    md.append(item["exp"])
    md.append("")
md.append("---")
md.append("")
md.append("## 声明")
md.append("")
md.append("本卷为根据本知识库既有真题考点自主命制的练习题，**不是真题**，不来自任何真实考试；"
          "参考答案为按教材与考点整理的要点，**非官方评分标准**，仅供考点串联与自测使用。")
md.append("")

# 写出
OUT_DIR.mkdir(parents=True, exist_ok=True)
html_path = OUT_DIR / f"{BASENAME}.html"
md_path = OUT_DIR / f"{BASENAME}.md"
html_path.write_text(html_out, encoding="utf-8")
md_path.write_text("\n".join(md), encoding="utf-8")

print("题量:", len(Q))
for tag, title in GROUPS:
    print(f"  {title}: {TAG_COUNT[tag]}")
print("答案分布:", Counter(x["ans"] for x in Q))
print("写入:", html_path)
print("写入:", md_path)
