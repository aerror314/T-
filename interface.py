import streamlit as st
from streamlit import session_state as ss
import asyncio
from style import style
from llm import LLM
from spider import Spider, LoginError, SecondVerificationError
from re import findall, DOTALL, match



def set_default():
    defaults = {"login_state": 0, "login_pwd_err": 0, "second_verify": 0, "username": "", "current_tab": "选课需求",
                "spider": None, "messages": [], "is_ai_thinking": False, "llm": None, "tabs": [], "required_courses": [],
                "preferred_courses": [], "sv_step": 0, 'sv_err': 0}
    for k, v in defaults.items():
        if k not in ss:
            setattr(ss, k, v)


def login_page():
    # print(f"#{ss.login_state}")

    login_col = st.columns(3)
    login_col[1].markdown("<h1>欢迎</h1>", unsafe_allow_html=True)
    login_col[1].markdown("<h6>请使用清华统一身份认证登录</h6>", unsafe_allow_html=True)
    ss.user_name = login_col[1].text_input("学号", placeholder="学号", key=f"login_name")
    ss.user_password = login_col[1].text_input("密码", placeholder="密码", key=f"login_password", type="password")
    if ss.login_pwd_err:
        login_col[1].markdown("❌ 学号或密码错误，请重试。")
    else:
        login_col[1].markdown("")
    if login_col[1].button("登录", width='stretch', type="primary"):
        try:
            ss.spider = spider = Spider(ss.user_name, ss.user_password, "2025-2026-2")
            spider.login()
            ss.llm = LLM(spider)
            ss.login_state = 1
            st.rerun()
        except LoginError:
            ss.login_pwd_err = 1
            st.rerun()
        except SecondVerificationError:
            ss.second_verify = 1
            ss.sv_step = 0
            st.rerun()


def second_verify():
    login_col = st.columns(3)
    login_col[1].markdown("<h1>二次验证</h1>", unsafe_allow_html=True)
    login_col[1].markdown("<h6>本次登录需要安全验证</h6>", unsafe_allow_html=True)
    if ss.sv_err:
        login_col[1].markdown("❌ 验证码错误或失效，请重试。")
    if ss.sv_step == 0:
        choice = login_col[1].selectbox("选择验证方式：", ['企业微信', '手机验证码'])
        if login_col[1].button("确认", key="second_verify_step_1"):
            if choice == '企业微信':
                ss.sv_step = 1
                ss.spider.second_verify(method="wechat")
                st.rerun()
            elif choice == '手机验证码':
                ss.sv_step = 1
                ss.spider.second_verify(method="mobile")
                st.rerun()
    else:
        vericode = login_col[1].text_input('请输入验证码')
        if login_col[1].button("确认", key="second_verify_step_2"):
            ss.sv_step = 0
            try:
                ss.spider.second_verify(vericode=vericode)
                ss.llm = LLM(ss.spider)
                ss.login_state = 1
                st.rerun()
            except SecondVerificationError:
                ss.sv_err = 1
                st.rerun()



async def main_navigation():
    st.sidebar.markdown("## THU 选课辅助")
    st.sidebar.markdown("---")

    # 定义导航项
    nav_items = [
        {"label": "📋 选课需求", "key": "选课需求"},
        {"label": "✨ 查看课表", "key": "查看课表"},
        {"label": "❓ 帮助 & 关于", "key": "帮助 & 关于"}
    ]

    # 显示导航项
    for item in nav_items:
        # 判断是否是当前选中的项
        is_active = ss.current_tab == item["key"]

        # 创建导航按钮
        if st.sidebar.button(
            item["label"],
            key=f"nav_{item['key']}",
            width='stretch',
            type="primary" if is_active else "secondary",
            disabled=ss.is_ai_thinking,
        ):
            ss.current_tab = item["key"]
            st.rerun()

    st.sidebar.markdown("---")


def get_prompt(limit, hint):
    prompt = "我是一名水木书院大一的学生，"
    if ss.required_courses:
        prompt += "本学期我必须要上的课有:"
        for re_course in ss.required_courses:
            if match(r'\d+', re_course):
                re_course += "(课程号)"
            prompt +=  re_course + ","
    if ss.preferred_courses:
        prompt += "除这些课程之外，我想要上的课有:"
        for pre_course in ss.preferred_courses:
            if match(r'\d+', pre_course):
                pre_course += "(课程号)"
            prompt += pre_course + ","
    prompt += f"本学期学分限制为{limit}学分，"
    if hint:
        prompt += "与此同时，我还有如下要求：" + hint
    prompt += "请帮我规划选课方案。"
    return prompt


async def main_page():
    st.markdown('<div class="main-title">THU 选课辅助系统</div>', unsafe_allow_html=True)
    st.markdown('<hr class="custom-hr">', unsafe_allow_html=True)

    main_col = st.columns([3, 1, 8])

    prompt = ""
    with main_col[0].container():
        credit_limit = st.number_input("学分限制", step=1, format="%d")
        col1 = st.columns([9, 1, 1])
        required_course = col1[0].text_input(
            "输入本学期 **必须** 要上的课程",
            disabled=ss.is_ai_thinking,
        )
        if col1[2].button('＋', key="required_course_add", type='tertiary'):
            ss.required_courses.append(required_course)
        if ss.required_courses:
            st.write("当前已输入：")
            with st.container():
                for i, course in enumerate(ss.required_courses[:]):
                    col = st.columns([8, 1, 2])
                    col[0].write(course)
                    if col[2].button('x', disabled=ss.is_ai_thinking, type="tertiary", key=f"required_course_{i}"):
                        ss.required_courses.remove(course)
                        st.rerun()
        col2 = st.columns([9, 1, 1])
        preferred_course = col2[0].text_input(
            "输入本学期 **您想要** 上的课程",
            disabled=ss.is_ai_thinking,
        )
        if col2[2].button('＋', key="preferred_course_add", type='tertiary'):
            ss.preferred_courses.append(preferred_course)
        if ss.preferred_courses:
            st.write("当前已输入")
            with st.container():
                for i, course in enumerate(ss.preferred_courses[:]):
                    col = st.columns([8, 1, 2])
                    col[0].write(course)
                    if col[2].button('x', disabled=ss.is_ai_thinking, type="tertiary", key=f"preferred_course_{i}"):
                        ss.preferred_courses.remove(course)
                        st.rerun()

        hints = st.text_area("您还有什么其它需求？", placeholder="例如：我不想上早八，我不想上晚上的课……",
                                  disabled=ss.is_ai_thinking)
        st.write("")
        if st.button("生成选课建议", width='stretch', type="primary", disabled=ss.is_ai_thinking):
            prompt += get_prompt(credit_limit, hints)

    with main_col[2].container():
        admit_user_table = st.checkbox('是否允许AI查看你的选课情况', disabled=ss.is_ai_thinking,
                                       value=ss.llm.admit_user_table)
        for message in ss.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"], unsafe_allow_html=True)
        if p:= main_col[2].chat_input("与AI对话……", disabled=ss.is_ai_thinking):
            prompt += p
        if prompt:
            ss.messages.append({"role": "user", "content": prompt})
            ss.is_ai_thinking = True
            ss.llm.add_message(prompt)
            ss.llm.admit_user_table = admit_user_table
            st.rerun()

        if ss.is_ai_thinking:
            with st.chat_message("assistant"):
                placeholder = st.empty()
                ans = ""
                tab = ""
                async for token, node in ss.llm.stream_response():
                    if node == 'agent':
                        ans += token
                    else:
                        tab += token
                    placeholder.markdown(ans + "▌", unsafe_allow_html=True)
                placeholder.markdown(ans, unsafe_allow_html=True)
                ss.messages.append({"role": "assistant", "content": ans})
                ss.is_ai_thinking = False

                print(tab)
                ss.tabs = findall(r"<TAB START>(.*?)</?TAB END>", tab, DOTALL)
                st.rerun()


def help_about():
    st.markdown('<div class="section-title">📖 使用说明</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="help-section">
    <h3>🎯 应用简介</h3>
    <p>这是一个针对 THU 学生开发的选课辅助系统，通过 AI 帮助您规划选课方案，满足您个性化的选课需求。</p >
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="help-section">
    <h3>📋 功能说明</h3>
    <h4>1. 选课需求</h4>
    <ul>
        <li>在此向 AI 描述您的选课需求。</li>
        <li>示例：我是一名水木书院大一的学生，本学期我们需要选的课有：中国近现代史纲要，写作与沟通，形势与政策，英语（阅读写作或者听说交流都可以）。能帮我规划一下课表吗？</li>
        <li>在与 AI 开始对话前，你可以选择是否允许AI查看你当前的选课情况。</p >
        <li>若您对 AI 生成的选课结果不满意，可在与 AI 对话来调整方案。</li>
    </ul>

    <h4>2. 查看课表</h4>
    <ul>
        <li>在 “选课需求” 界面与 AI 对话后，AI 会自动生成可视化课表。</li>
        <li>AI会在课程表后添加补充信息。</li>
    </ul>

    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="help-section">
    <h3>⚡ 注意</h3>
    <ul>
        <li>由于开发时间较紧，目前该选课辅助系统仍存在较多局限。</li>
        <li>该系统数据来源为2025-2026学年第二学期补退选阶段的课程数据。</li>
        <li>因此该系统针对预选阶段的课容量进行规划的能力可能有限（尚无数据进行充分测试）。</li>
        <li>同时由于 THU 的选课规则较为复杂，AI 有可能生成显然存在错误的方案（如时间冲突，给必上的课用第一志愿等），需在后续对话中调整。</li>
        <li>注意 AI 生成内容时不要轻易刷新页面，可能导致已生成的数据丢失。</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="help-section">
    <h3>✅ 关于</h3>
    <ul>
        <li>作者：吴俊宇，邱信杰，周王瑞</li>
        <li>联系方式：3696178048@qq.com，1050570706@qq.com，（*）</li>
        <li>感谢您使用本产品。系统尚不完善，许多功能有待开发，敬请谅解。</li>
        <li>若发现bug，欢迎向作者反馈。再次感谢您的支持！</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)


async def show_schedule():
    st.markdown('<div class="main-title">推荐课表</div>', unsafe_allow_html=True)
    st.markdown('<hr class="custom-hr">', unsafe_allow_html=True)
    if not ss.tabs:
        st.markdown('暂无推荐的课程表，你可以先让AI生成一份')
    else:
        for tab in ss.tabs:
            st.markdown(tab, unsafe_allow_html=True)
            st.markdown('<hr class="custom-hr">', unsafe_allow_html=True)


async def main():
    st.markdown(style, unsafe_allow_html=True)
    set_default()

    if ss.login_state == 0:
        if not ss.second_verify:
            login_page()
        else:
            second_verify()
    else:
        await main_navigation()
        if ss.current_tab == "选课需求":
            await main_page()
        elif ss.current_tab == "查看课表":
            await show_schedule()
        elif ss.current_tab == "帮助 & 关于":
              help_about()


if __name__ == "__main__":
    asyncio.run(main())
