style = """
<style>
    /* 主标题样式 */
    .main-title {
        font-size: 4rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* 副标题样式 */
    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1e1e1e;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        padding-left: 10px;
    }
    
    /* 表格头部样式 */
    .table-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.3rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* 事件行样式 */
    .event-row {
        padding: 0.8rem;
        margin: 0.3rem 0;
        border-radius: 8px;
        transition: all 0.3s ease;
        border-left: 4px solid transparent;
    }
    
    .event-row:hover {
        background-color: #f8f9fa;
        transform: translateX(5px);
    }
    
    .completed-event {
        background-color: #f0f8f0;
        border-left-color: #28a745;
        opacity: 0.7;
    }
    
    .high-priority {
        border-left-color: #dc3545;
        background-color: #fff5f5;
    }
    
    .medium-priority {
        border-left-color: #ffc107;
        background-color: #fffbf0;
    }
    
    .low-priority {
        border-left-color: #28a745;
        background-color: #f8fff8;
    }
    
    /* 按钮样式 */
    .stButton>button {
        border-radius: 20px;
        border: none;
        transition: all 0.3s ease;
    }
            
    /* 主按钮样式 */
    button[kind="primary"] {
        background-color: #6D29FF !important;
        color: white !important;
    }
    
            
    button[kind="primary"]:hover {
        background-color: #8343FF !important;
        transform: translateY(-2px);
    }
    
    /* 次要按钮样式 */
    button[kind="secondary"] {
        background-color: #3C3E57 !important;
        color: white !important;
    }
    
    button[kind="secondary"]:hover {
        background-color: #515475 !important;
        transform: translateY(-2px);
    }
    
    
    /* 输入框样式 */
    .stTextInput>div>div>input, 
    .stTextArea>div>div>textarea {
        border-radius: 10px;
    }
    
    /* 分割线样式 */
    .custom-hr {
        margin: 0.5rem 0;
        border: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
    }
    
    /* 状态指示器 */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-pending { background-color: #ffc107; }
    .status-in-progress { background-color: #17a2b8; }
    .status-completed { background-color: #28a745; }
    
    /* 时间显示样式 */
    .time-display {
        font-family: 'Courier New', monospace;
        font-size: 0.9em;
        padding: 2px 6px;
        border-radius: 4px;
        background-color: #232424;
    }
    
    .time-overdue {
        color: #F78B88;
        background-color: #232424;
        font-weight: bold;
    }
    
    .time-upcoming {
        color: #FFC69D;
        background-color: #232424;
        font-weight: bold;
    }
            
    .time-normal {
        color: #E6FFCB;
        background-color: #232424;
    }
            
    .time-finished {
        color: #303030;
        background-color: #0F1116;
    }
    
    /* 侧边栏样式 */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2d2d2d 0%, #1a1a1a 100%);
    }
    
    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #2d2d2d;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
    }
    
    /* 帮助页面样式 */
    .help-section {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    
    /* 自定义导航按钮样式 */
    .nav-button {
        width: 100%;
        margin: 5px 0;
        border-radius: 10px;
        transition: all 0.3s ease;
        background-color: #272430;
    }
    
    .nav-button-active {
        background-color: #667eea !important;
        color: white !important;
    }
    
    /* 排序选择框样式 */
    .sort-select {
        background-color: #2d2d2d;
        border-radius: 8px;
        padding: 5px 10px;
        border: 1px solid #444;
    }
            
</style>
"""