import streamlit as st
import base64
from utils import validate_email

# __order__ = 2
def get_image_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


VoiceDecoder = get_image_base64("VoiceDecoder.png")
SourceTracker = get_image_base64("SourceTracker.png")
KeyScanner = get_image_base64("KeyScanner.png")


def app():
    # 自定义CSS样式 - 蓝色主题
    st.markdown("""
    <style>
        /* 主容器样式 */
        .main {
            background-color: #f5f7fa;
        }

        /* 标题样式 */
        .header {
            background: linear-gradient(90deg, #3f51b1, #3f51b5);
            color: white;
            padding: 20px;
            border-radius: 0;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);    
        }

        /* 卡片样式 */
        .card {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 25px;
            margin-bottom: 20px;
            transition: all 0.3s ease;
            border-left: 4px solid #3f51b5;
        }

        .card:hover {
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transform: translateY(-3px);
        }

        /* 按钮样式 */
        .stButton>button {
            background-color: #3f51b5;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 10px 24px;
            font-weight: 500;
            width: 100%;
            transition: all 0.3s;
        }

        .stButton>button:hover {
            background-color: #303f9f;
            transform: translateY(-2px);
        }

        /* 页脚样式 */
        .footer {
            text-align: center;
            padding: 1.5rem;
            margin-top: 3rem;
            color: #666;
            font-size: 0.9rem;
            border-top: 1px solid #eee;
        }

        /* 联系表单样式 */
        .contact-form input, 
        .contact-form textarea {
            width: 100%;
            padding: 12px;
            border: 1px solid #ccc;
            border-radius: 4px;
            margin: 8px 0;
            font-size: 1rem;
        }

        .contact-form button {
            background-color: #3f51b5;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: 500;
            margin-top: 8px;
            transition: all 0.3s;
        }

        .contact-form button:hover {
            background-color: #303f9f;
        }
    </style>
    """, unsafe_allow_html=True)

    # 页面标题区
    st.markdown('''
    <div class="header">
        <h1>信源话语传播效果评估系统</h1>
        <p style="font-size:22px; font-style: italic; color: white; margin-top: -10px;">
            Discourse Communication Effectiveness Evaluation System for Information Source
        </p>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown("""
        <style>
        .welcome-card {
            background: linear-gradient(145deg, #ffffff 0%, #f1f3f9 100%);;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 6px 24px rgba(63, 81, 181, 0.1);
            margin-bottom: 2.5rem;
            border-left: 5px solid #3f51b5;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
            overflow: hidden;
        }
        
        .welcome-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 24px rgba(0,0,0,0.12);
        }
        .welcome-title {
            color: #3f51b5;
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 10px;
        }
        .welcome-subtitle {
            color: #495057;
            font-size: 1.15rem;
            line-height: 1.6;
            margin-bottom: 10px;
        }
        .welcome-highlight {
            color: #3f51b5;
            font-weight: 500;
        }
        </style>
        <div class="welcome-card">
            <div class="welcome-subtitle">本系统由上海交通大学外国语学院郇昌鹏教授团队研发，基于前沿数据算法，科学量化评估中国声音话语传播效果。</div>  
            <div class="welcome-title">搭载智能外语芯，以语言数据驱动智慧决策，让中国声音更响亮！ 🎙️</div>  
        </div>
    """, unsafe_allow_html=True)

    # 功能模块卡片
    st.markdown('<h3 style=" color: #3f51b5;">关键功能模块</h3>', unsafe_allow_html=True)

    cols = st.columns(3)
    with cols[0]:
        st.markdown(f"""
        <div class="card">
            <h3>
                <img src="data:image/png;base64,{KeyScanner}" 
                style="width:43px; height:40px; vertical-align:middle; margin-right:8px;">
                <span style="vertical-align:middle; font-size: 1.6rem; color: #000000;">提取核心声量</span>
            </h3>
            <h3 style="color: #3f51b5; margin-left: 00px;">KeyScanner</h3>
            <p>基于高频关键词和聚类分析的文本过滤引擎，精准锁定中国声音核心语料。</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("进入声量提取", key="corre_btn"):
            st.session_state.current_page = "声量提取"
            st.rerun()

    with cols[1]:
        st.markdown(f"""
        <div class="card">
            <h3>
                <img src="data:image/png;base64,{SourceTracker}" 
                style="width:43px; height:40px; vertical-align:middle; margin-right:8px;">
                <span style="vertical-align:middle; font-size: 1.6rem; color: #000000;">追踪声源脉络</span>
            </h3>
            <h3 style="color: #3f51b5; margin-left: 00px;">SourceTracker</h3>
            <p>全文声源语句抓取系统，结构化标注声源归属，构建中国话语传播链路地图。</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("进入脉络追踪", key="extract_btn"):
            st.session_state.current_page = "脉络追踪"
            st.rerun()

    with cols[2]:
        st.markdown(f"""
        <div class="card">
            <h3>
                <img src="data:image/png;base64,{VoiceDecoder}" 
                style="width:43px; height:40px; vertical-align:middle; margin-right:8px;">
                <span style="vertical-align:middle; font-size: 1.6rem; color: #000000;">探析声效传播</span>
            </h3>
            <h3 style="color: #3f51b5; margin-left: 00px;">VoiceDecoder</h3>
            <p>基于语篇语义和词汇语法的话语功能解码系统，量化中国声源国际传播效力。</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("进入传播探析", key="attribu_btn"):
            st.session_state.current_page = "传播探析"
            st.rerun()

    st.markdown("---")

    # 快速指南
    with st.expander("📋 使用指南", expanded=True):
        st.markdown("""
        <div style="padding: 1rem;">
            <h4 style="color: #3f51b5;">系统使用步骤</h4>
            <ol style="line-height: 2;">
                <li><strong>选择分析模块</strong>：点击上方功能卡片进入相应模块</li>
                <li><strong>上传数据</strong>：支持Excel、CSV或直接文本输入</li>
                <li><strong>设置参数</strong>：根据需求调整分析维度</li>
                <li><strong>查看结果</strong>：系统自动生成可视化报告</li>
            </ol>
            <p style="margin-top: 1rem;">点击左上角">"按钮可展开侧边栏菜单</p>
        </div>
        """, unsafe_allow_html=True)

    # 联系信息
    st.markdown("---")
    with st.expander("📧 联系我们", expanded=True):
        st.markdown("""
        <div style="padding: 1rem;">
            <h4 style="color: #3f51b5;">技术合作与咨询</h4>
            <ul style="margin-left: 20px; line-height: 1.8;">
                <li>如有任何问题或合作意向，请联系研发团队</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # 增加 contact_form 缩进
        st.markdown('<div style="margin-left: 40px;">', unsafe_allow_html=True)

        with st.form("contact_form"):
            name = st.text_input("您的姓名", placeholder="请输入您的姓名")
            email = st.text_input("您的邮箱", placeholder="请输入您的邮箱")
            message = st.text_area("您的留言", placeholder="请输入您的留言")
            submit_button = st.form_submit_button("发送")

            if submit_button:
                if not name:
                    st.warning("⚠️ 请填写您的姓名！")
                elif not email:
                    st.warning("⚠️ 请填写您的邮箱！")
                elif not validate_email(email):
                    st.error("❌ 请输入有效的邮箱地址！")
                elif not message:
                    st.warning("⚠️ 请填写您的留言！")
                else:
                    st.success("✅ 消息已成功提交！")

        st.markdown('</div>', unsafe_allow_html=True)

        # 使用内联CSS美化表单
        st.markdown("""
            <style>
                input[type=text], input[type=email], textarea {
                    width: 100%;
                    padding: 12px;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    box-sizing: border-box;
                    margin-top: 6px;
                    margin-bottom: 16px;
                    resize: vertical;
                }
                textarea {
                    height: 150px;
                }
            </style>
            """, unsafe_allow_html=True)

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


if __name__ == "__main__":
    app()