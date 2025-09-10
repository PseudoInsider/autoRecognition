import os
import shutil
import tempfile
import pandas as pd
import streamlit as st
from predict import IOTagger
import base64

# __order__ = 8
def get_image_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


VoiceDecoder = get_image_base64("VoiceDecoder.png")

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
        color: {PRIMARY_COLOR};
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

    /* 隐藏模型路径输入 */
    .model-path-input {{
        display: none;
    }}
    </style>
    """, unsafe_allow_html=True)


# 定义全局颜色变量
PRIMARY_COLOR = "#3f51b5"
SECONDARY_COLOR = "#5c6bc0"
BG_COLOR = "#f8f9fa"
TEXT_COLOR = "#333333"


# Step 3: Sequence Labeling
def app():
    # Initialize session state variables at the very beginning
    if 'predicted_data' not in st.session_state:
        st.session_state.predicted_data = None
    apply_custom_styles()
    VoiceDecoder = get_image_base64("VoiceDecoder.png")


    st.markdown(
        f"""
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&family=Noto+Sans+SC:wght@400;700&display=swap');
                .title-container {{
                    text-align: center;
                    margin: 0 auto 2rem;
                    max-width: 800px;
                    padding: 1.5rem;
                    border-radius: 12px;
                    background: #f8f9fa;
                }}
                .title-with-logo {{
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 15px;
                    margin-bottom: 0.5rem;
                }}
                .main-title {{
                    font-family: 'Noto Sans SC', sans-serif;
                    font-size: 2.2rem;
                    color: #263238;
                    letter-spacing: 1px;
                    margin: 0;
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

            <div class="title-container">
                <div class="title-with-logo">
                    <img src="data:image/png;base64,{VoiceDecoder}" class="logo-img">
                    <h1 class="main-title">探析声效传播</h1>
                </div>
                <h2 class="sub-title">VocieDecoder</h2>
                <p class="description">
                    结合语篇语义与词汇语法（局部语法、依存语法和型式语法）的中国话语功能解码系统，量化中国声音的国际传播效力。
                </p>
            </div>
            """,
        unsafe_allow_html=True
    )

    # Allow user to upload CSV or use preprocessed data from Step 2
    with st.container():
        st.markdown('<div class="section-title">🔄 数据输入</div>', unsafe_allow_html=True)
        input_option = st.radio(
            "输入源:",
            ["上传【脉络追踪】输出CSV文件"],
            label_visibility="collapsed"
        )
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

        if input_option == "上传【脉络追踪】输出CSV文件":
            uploaded_file = st.file_uploader("上传CSV文件进行分析", type=["csv"])
            if uploaded_file:
                df_input = pd.read_csv(uploaded_file)
        else:
            if 'preprocessed_data' in st.session_state and st.session_state.preprocessed_data is not None:
                df_input = st.session_state.preprocessed_data

    # Model settings section
    with st.container():
        st.markdown('<div class="section-title">🤖 模型加载</div>', unsafe_allow_html=True)

        # Centered notification card
        with st.container():
            col1, col2, col3 = st.columns([1, 6, 1])
            with col2:
                st.markdown(
                    '''
                    <div class="custom-card" style="text-align: center;">
                        <p class="custom-label">效果评估V1模型已顺利加载</p>
                        <p style="color: #666; margin-top: 8px;">将对文本的话语功能进行深入解剖，点击下方按钮开始分析</p>
                    </div>
                    ''',
                    unsafe_allow_html=True
                )

        # Hidden model configuration
        model_path = "V1-model.bin"

        # Centered analysis button with processing logic
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("运行局部语法分析",
                         use_container_width=True,
                         help="点击开始分析文本的话语功能"):

                # Model validation
                if not os.path.exists(model_path):
                    st.error(f"❌ 模型文件未找到: {model_path}")
                    st.stop()

                # Create temporary workspace
                with st.spinner("准备分析环境..."):
                    temp_dir = tempfile.mkdtemp()
                    input_csv = os.path.join(temp_dir, "input.csv")
                    df_input.to_csv(input_csv, index=False)

                # Analysis execution with progress
                progress_text = "正在进行深度分析..."
                progress_bar = st.progress(0, text=progress_text)
                status_text = st.empty()

                try:
                    # Initialize analyzer
                    tagger = IOTagger(model_path=model_path)

                    # Simulation of analysis process
                    for percent in range(100):
                        # Update progress
                        progress_bar.progress(percent + 1)
                        status_text.text(f"{progress_text} {percent + 1}%")

                        # Actual processing at the end
                        if percent == 99:
                            results = tagger.predict_dataset(input_csv=input_csv)
                            st.session_state.predicted_data = pd.DataFrame(results)

                    # Success notification
                    st.balloons()
                    status_text.success("✅ 分析完成! 结果已准备就绪")

                except Exception as e:
                    st.error(f"⚠️ 分析中断: {str(e)}")
                    if 'temp_dir' in locals():
                        shutil.rmtree(temp_dir, ignore_errors=True)
                finally:
                    progress_bar.empty()
                    if 'status_text' in locals():
                        status_text.empty()

    # Display and download results
    if st.session_state.predicted_data is not None:
        with st.container():
            st.markdown('<div class="section-title">🔍 ️局部语法</div>', unsafe_allow_html=True)
            st.dataframe(st.session_state.predicted_data.head())

            csv = st.session_state.predicted_data.to_csv(index=False).encode('utf-8')
            st.download_button(
                "下载分析数据 (CSV)",
                csv,
                file_name="labeled_results.csv",
                mime="text/csv"
            )

            # Show sample tagged sentences
            st.markdown('<div class="section-title">📝 分析示例</div>', unsafe_allow_html=True)

            # 使用columns布局让选择框更紧凑
            col1, _ = st.columns([0.3, 0.7])  # 使用下划线忽略第二列
            with col1:
                sample_idx = st.selectbox(
                    "选择要查看的话语",
                    range(len(st.session_state.predicted_data)),
                    key="sample_select"
                )

        # 主内容区域
        with st.container():
            sample = st.session_state.predicted_data.iloc[sample_idx]

            # 使用卡片样式
            st.markdown(
                f'''
                <div class="custom-card flat-card">
                    <h4 class="card-header">原文内容</h4>
                    <div class="card-content">
                        {sample['ReportingSentence']}
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )
            COLOR_MAP = {
                "cue": "#FF6B6B",  # 红色
                "source": "#4ECDC4",  # 青绿色
                "content": "#45A7E6",  # 蓝色
                "hinge": "#FFA07A",  # 橙色
                "residue": "#A5D8A7"  # 绿色
            }
            # 分析结果卡片
            tagged_text = sample['tagged_sentences'].replace('<', '&lt;').replace('>', '&gt;')
            st.markdown(
                f'''
                <div class="custom-card flat-card">
                    <h4 class="card-header">分析结果</h4>
                    <div class="card-content">
                        {tagged_text}
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )
            # 话语功能卡片 - 使用更简洁的布局
            st.markdown(
                f'''
                <div class="custom-card flat-card">
                    <h4 class="card-header">话语功能分析</h4>
                    <div class="function-grid">
                        <div class="function-item">
                            <span class="function-label" style="color:{COLOR_MAP["cue"]}">
                            提示词 (cue):</span>
                            <span class="function-value" style=" {COLOR_MAP["cue"]}">
                                {sample.get("cue", "无")}</span>
                        </div>
                        <div class="function-item">
                            <span class="function-label" style="color:{COLOR_MAP["source"]}">
                            来源 (source):</span>
                            <span class="function-value" style=" {COLOR_MAP["source"]}">
                                {sample.get("source", "无")}</span>
                        </div>
                        <div class="function-item">
                            <span class="function-label" style="color:{COLOR_MAP["content"]}">
                            内容 (content):</span>
                            <span class="function-value" style=" {COLOR_MAP["content"]}">
                                {sample.get("content", "无")}</span>
                        </div>
                        <div class="function-item">
                            <span class="function-label" style="color:{COLOR_MAP["hinge"]}">
                            连接词 (hinge):</span>
                            <span class="function-value" style=" {COLOR_MAP["hinge"]}">
                                {sample.get("hinge", "无")}</span>
                        </div>
                        <div class="function-item">
                            <span class="function-label" style="color:{COLOR_MAP["residue"]}">
                            剩余部分 (residue):</span>
                            <span class="function-value" style=" {COLOR_MAP["residue"]}">
                                {sample.get("residue", "无")}</span>
                        </div>
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )

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
                    <div style="font-size: 0.9rem;">
                        郇昌鹏 & 王玲玲｜研发
                    </div>
                    <div style="font-size: 0.75rem; margin-top: 0.8rem; color: #888;">
                        版本号: V1.0 | 最后更新: 2025年4月
                    </div>
                </div>
                """, unsafe_allow_html=True)

