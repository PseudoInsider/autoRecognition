import streamlit as st
import homePage
import correPage
import extractPage
import attribuPage


# __order__ = 1
# 页面配置（在最前）
st.set_page_config(
    page_title="信源话语传播效果评估系统",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 定义页面顺序
PAGES = {
    "主页": homePage,
    "声量提取": correPage,
    "脉络追踪": extractPage,
    "传播探析": attribuPage
}
PAGE_ORDER = list(PAGES.keys())

# 修改后的侧边栏控制逻辑
with st.sidebar:
    # 展开时显示页面选择器
    if st.session_state.get("sidebar_state") != "collapsed":
        st.title("导航菜单")
        # 添加页面选择器（下拉菜单形式）
        selection = st.selectbox(
            "请选择页面",
            list(PAGES.keys()),
            index=PAGE_ORDER.index(st.session_state.get("current_page", "主页"))
        )
        # 更新当前页面状态
        if selection != st.session_state.get("current_page"):
            st.session_state.current_page = selection
            st.rerun()

        # 添加导航按钮
        current_index = PAGE_ORDER.index(st.session_state.get("current_page", "主页"))
        col1, col2 = st.columns(2)

        # 从第二页开始显示"上一页"按钮
        if current_index > 0:
            with col1:
                if st.button("上一页"):
                    st.session_state.current_page = PAGE_ORDER[current_index - 1]
                    st.rerun()

        # 如果不是最后一页，显示"下一页"按钮
        if current_index < len(PAGE_ORDER) - 1:
            with col2:
                if st.button("下一页"):
                    st.session_state.current_page = PAGE_ORDER[current_index + 1]
                    st.rerun()

        # 关闭内容区
        st.markdown('</div>', unsafe_allow_html=True)


# 页面路由逻辑
current_page = st.session_state.get("current_page", "主页")
page = PAGES[current_page]
page.app()