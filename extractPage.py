import os
import shutil
import tempfile
import zipfile
import pandas as pd
from preprocessing import PreprocessText
import streamlit as st
import base64

# __order__ = 6
def get_image_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


SourceTracker = get_image_base64("SourceTracker.png")

# 定义全局颜色变量
PRIMARY_COLOR = "#3f51b5"
SECONDARY_COLOR = "#5c6bc0"
BG_COLOR = "#f8f9fa"
TEXT_COLOR = "#333333"


def apply_custom_styles():
    st.markdown(f"""
    <style>
    /* 基础样式 */
    .stApp {{
        background-color: {BG_COLOR};
    }}

    /* 主标题样式 */
    .main-title {{
        font-size: 2.5rem;
        color: {PRIMARY_COLOR};
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 600;
        letter-spacing: 1px;
    }}

    /* 分区标题样式 */
    .section-title {{
        font-size: 1.4rem;
        color: {TEXT_COLOR};
        padding: 0.8rem 1.2rem;
        background: linear-gradient(90deg, {PRIMARY_COLOR} 0%, {SECONDARY_COLOR} 100%);
        color: white;
        border-radius: 8px;
        margin: 2rem 0 1.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}

    /* 卡片容器样式 */
    .custom-card {{
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 4px solid {PRIMARY_COLOR};
    }}

    /* 文件上传区域样式 */
    .upload-area {{
        border: 2px dashed {PRIMARY_COLOR};
        border-radius: 5px;
        padding: 20px;
        text-align: center;
        background-color: rgba(63,81,181,0.05);
        margin: 1rem 0;
        transition: all 0.3s;
    }}
    .upload-area:hover {{
        background-color: rgba(63,81,181,0.1);
    }}

    /* 按钮样式 */
    .stButton>button {{
        background: {PRIMARY_COLOR};
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        border: none;
        transition: all 0.3s;
    }}
    .stButton>button:hover {{
        background: {SECONDARY_COLOR};
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(63,81,181,0.2);
    }}

    /* 标签样式 */
    .custom-label {{
        font-weight: 600;
        color: {PRIMARY_COLOR};
        margin-bottom: 0.5rem;
    }}

    /* 选项卡样式 */
    .stTabs [role=tablist] button {{
        color: {TEXT_COLOR};
    }}
    .stTabs [role=tablist] button[aria-selected=true] {{
        color: {PRIMARY_COLOR};
        border-bottom: 2px solid {PRIMARY_COLOR};
    }}

    /* 数据表格样式 */
    .stDataFrame {{
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}
    </style>
    """, unsafe_allow_html=True)


# 初始化 session state
if 'china_results' not in st.session_state:
    st.session_state.china_results = None


def app():
    """声音探查子页面"""
    # 应用自定义样式
    apply_custom_styles()

    # 初始化session_state
    if 'preprocessed_data' not in st.session_state:
        st.session_state.preprocessed_data = None
    # 初始化 session state
    if "temp_dir" not in st.session_state:
        st.session_state.temp_dir = tempfile.mkdtemp()
    if "uploader_key_counter" not in st.session_state:
        st.session_state.uploader_key_counter = 0

    # 主标题
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;500;700&family=Noto+Sans+SC:wght@500;700&display=swap');

            .source-tracker-container {{
                text-align: center;
                max-width: 800px;
                margin: 0 auto 2rem;
                padding: 1.5rem;
                border-radius: 12px;
                background: #f8f9fa;
            }}

            .header-with-logo {{
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 12px;
                margin-bottom: 0.5rem;
            }}

            .main-title {{
                font-family: 'Noto Sans SC', sans-serif;
                font-size: 2.2rem;
                font-weight: 700;
                color: #3f51b5;
                margin: 0;
                display: flex;
                align-items: center;
            }}

            .logo-img {{
                    width: 50px;
                    height: 50px;
                    object-fit: contain;
                }}
                .sub-title {{
                    font-family: 'Roboto', sans-serif;
                    font-size: 2rem;
                    margin: 0.5rem 0;
                    font-weight: 700;
                    background: linear-gradient(90deg, #3f51b5, #5c6bc0);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }}
                .description {{
                    font-family: 'Noto Sans SC', sans-serif;
                    text-align: center;
                    color: #666;
                    transform: translateX(100px);
                    margin: 1.5rem auto;
                    max-width: 600px;
                    line-height: 1.7;
                    font-size: 1.1rem;
                    padding: 0 1rem;
                }}
        </style>

        <div class="source-tracker-container">
            <div class="header-with-logo">
                <img src="data:image/png;base64,{SourceTracker}" class="logo-img">
                <h1 class="main-title">追踪声源脉络</h1>
            </div>
            <h2 class="sub-title">SourceTracker</h2>
            <p class="description">
                全文本声源语句抓取系统，结构化标注声源归属，构建话语传播链路地图。
            </p>
        </div>
    """, unsafe_allow_html=True)

    # ========== 文件输入部分 ==========
    with st.container():
        st.markdown('<div class="section-title">📁 文件输入</div>', unsafe_allow_html=True)

        # 输入源选择
        with st.container():
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown('<div class="custom-label">选择输入源:</div>', unsafe_allow_html=True)
            with col2:
                input_option = st.radio(
                    " ",  # 改为单个空格
                    ["上传关联达标文件"],
                    horizontal=True,
                    label_visibility="collapsed",
                    key="input_source_radio"
                )

        # 初始化 session_state 变量
        if 'uploader_key_counter' not in st.session_state:
            st.session_state.uploader_key_counter = 0
        if 'temp_dir' not in st.session_state:
            st.session_state.temp_dir = None

        current_uploader_key = f"file_uploader_{st.session_state.uploader_key_counter}"

        # 文件上传处理
        if input_option == "上传关联达标文件":
            with st.container():
                # 更清晰的拖拽区域提示
                st.markdown("""
                <style>
                    .upload-area {
                        border: 2px dashed #3f51b5;
                        border-radius: 5px;
                        padding: 20px;
                        text-align: center;
                        background-color: #f9f9f9;
                        margin-bottom: 10px;
                    }
                </style>
                <div class="upload-area">
                    <p style="text-align: center; margin: 1em 0; color: #666;">
                        ↓ 点击或拖拽文件到下方区域 ↓
                    </p>
                """, unsafe_allow_html=True)

                # 修改文件上传组件
                uploaded_files = st.file_uploader(
                    " ",  # 改为单个空格
                    type=["txt"],
                    accept_multiple_files=True,
                    help="支持上传多个文本文件(.txt格式)",
                    key=current_uploader_key,
                    label_visibility="collapsed"
                )
            # 操作按钮组
            st.markdown("""
            <style>
            .stButton > button {
                height: 100% !important;
                min-height: 55px;
                padding-top: 12px !important;
                padding-bottom: 12px !important;
            }
            [data-testid="column"] {
                align-self: stretch !important;
            }
            </style>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns([4, 1.2], gap="small")

            with col1:
                status_msg = uploaded_files and f"✅ 已成功上传 {len(uploaded_files)} 个文件" or "📤 等待文件上传..."
                st.info(status_msg)

            with col2:
                if st.button("🗑️ 清空缓存",
                             disabled=not uploaded_files and not st.session_state.temp_dir,
                             use_container_width=True):
                    # 清理临时目录
                    if st.session_state.temp_dir and os.path.exists(st.session_state.temp_dir):
                        shutil.rmtree(st.session_state.temp_dir, ignore_errors=True)

                    # 重置状态
                    st.session_state.temp_dir = None
                    st.session_state.uploader_key_counter += 1

                    if "china_results" in st.session_state:
                        del st.session_state.china_results

                    st.rerun()
            # 如果存在上传文件才显示后续内容
            if uploaded_files:
                # 确保临时目录存在
                if st.session_state.temp_dir is None:
                    st.session_state.temp_dir = tempfile.mkdtemp()

                # 保存文件到临时目录
                temp_dir = st.session_state.temp_dir
                try:
                    for file in uploaded_files:
                        file_path = os.path.join(temp_dir, file.name)
                        with open(file_path, "wb") as f:
                            f.write(file.getbuffer())
                        # 处理ZIP文件
                        if file.name.lower().endswith('.zip'):
                            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                                zip_ref.extractall(temp_dir)
                            os.remove(file_path)
                except Exception as e:
                    st.error(f"文件保存失败: {str(e)}")
                    st.stop()  # 停止执行后续代码

                # ========== 预处理设置部分 ==========
                with st.container():
                    st.markdown('<div class="section-title">⚙️ 预处理设置</div>', unsafe_allow_html=True)

                    with st.container():
                        with st.container():
                            st.markdown(
                                '''
                                <div class="custom-card"> 
                                追踪预处理支持设置上下文语境长短和单项声源内容复合度。
                                </p></div>
                                ''',
                                unsafe_allow_html=True
                            )

                            cols = st.columns(2)
                            with cols[0]:
                                st.markdown('<div class="custom-label">上下文范围</div>', unsafe_allow_html=True)
                                context_range = st.slider(
                                    "",
                                    1, 10, 3,
                                    help="确定在报道动词前后提取多少句上下文",
                                    key="preprocess_context_range",
                                    label_visibility="collapsed"
                                )

                            with cols[1]:
                                st.markdown('<div class="custom-label">最大合并句子数</div>', unsafe_allow_html=True)
                                max_merge = st.slider(
                                    "",
                                    1, 5, 3,
                                    help="确定最多合并多少相邻句子",
                                    key="preprocess_max_merge",
                                    label_visibility="collapsed"
                                )

                            st.markdown('</div>', unsafe_allow_html=True)

                # ========== 操作按钮 ==========
                with st.container():
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        if st.button("🚀 运行脉络追踪", key="run_preprocess", use_container_width=True):
                            if not os.path.exists(temp_dir) or not os.listdir(temp_dir):
                                st.error("没有找到可处理的文件")
                            else:
                                # 修改这部分代码：
                                config = {
                                    'context_range': context_range,
                                    'max_merge': max_merge,
                                    'reporting_verbs_file': os.path.join(os.path.dirname(__file__),
                                                                         'reporting_verbs.csv'),
                                    'output_directory': tempfile.mkdtemp(),
                                    'input_directory': temp_dir
                                }

                                with st.spinner("正在处理文本，请稍候..."):
                                    try:
                                        preprocessor = PreprocessText(config)
                                        preprocessor.preprocess_text()

                                        # 修正这里 - 明确指定输出文件名
                                        output_path = os.path.join(config['output_directory'], "output.csv")
                                        if os.path.exists(output_path):
                                            df_preprocessed = pd.read_csv(output_path)
                                            st.session_state.preprocessed_data = df_preprocessed
                                            st.success("处理完成!")
                                        else:
                                            st.error(f"未找到输出文件，预期路径: {output_path}")
                                    except Exception as e:
                                        st.error(f"处理过程中出错: {str(e)}")

                # ========== 结果显示部分 ==========
                if 'preprocessed_data' in st.session_state and st.session_state.preprocessed_data is not None:
                    st.markdown('<div class="section-title">📊 追踪结果</div>', unsafe_allow_html=True)

                    with st.container():
                        tab1, tab2 = st.tabs(["数据预览", "数据统计"])

                        with tab1:
                            with st.container():
                                st.markdown(
                                    '''
                                    <div class="custom-card"> 
                                    全文本声源语句抓取，结构化标注声源归属。
                                    </p></div>
                                    ''',
                                    unsafe_allow_html=True
                                )
                                st.write("前5行示例:")
                                st.write(st.session_state.preprocessed_data.head())
                                st.markdown('</div>', unsafe_allow_html=True)

                        with tab2:
                            with st.container():
                                cols = st.columns(1)
                                with cols[0]:
                                    st.markdown(
                                        '''
                                        <div class="custom-card"> 
                                        追踪结果如下，支持提取文本名称、上下文语境和声源内容，保存在csv文件中。
                                        </p></div>
                                        ''',
                                        unsafe_allow_html=True
                                    )
                                    st.markdown("**数据概览**")
                                    st.write(
                                        f"经过数据分析，共提取 <b><span style='color: red;'>{len(st.session_state.preprocessed_data)}</span></b> 行声源记录。",
                                        unsafe_allow_html=True
                                    )
                                    st.write("后5行示例:")
                                    st.write(st.session_state.preprocessed_data.tail())
                                    st.markdown('</div>', unsafe_allow_html=True)

                    # 下载按钮
                    with st.container():
                        st.markdown('<div style="text-align:center;margin-top:2rem;">', unsafe_allow_html=True)
                        st.download_button(
                            label="⬇️ 下载追踪结果 (CSV)",
                            data=st.session_state.preprocessed_data.to_csv(index=False).encode('utf-8'),
                            file_name="preprocessed_data.csv",
                            mime="text/csv",
                            key="download_preprocessed",
                            use_container_width=True,
                            help="下载处理后的CSV文件"
                        )
                        st.markdown('</div>', unsafe_allow_html=True)

        # 页脚 - 制作单位信息
        st.markdown("""
                    <style>
                        .footer {
                            text-align: center;
                            padding: 1.5rem 1rem;
                            color: #555;
                            border-top: 1px solid #eee;
                            transition: all 0.3s;
                        }
                        .footer:hover {
                            color: #333;
                            background: #f9f9f9;
                        }
                    </style>

                    <div class="footer">
                          <p style="margin-bottom: 0.5rem;"><strong>© 2025 信源话语传播效果评估系统</strong></p>
                        <div style="font-size: 0.7rem;">
                            郇昌鹏 & 王玲玲｜研发
                        </div>
                        <div style="font-size: 0.75rem; margin-top: 0.8rem; color: #888;">
                            版本号: V1.0 | 最后更新: 2025年4月
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
