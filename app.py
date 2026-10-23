import tempfile
import hashlib
import shutil
from pathlib import Path
from urllib.parse import quote_plus
import streamlit as st
from core import read_document, facts, report

st.set_page_config(page_title='Planning Agent 1.0', layout='wide')
st.title('Planning Agent 1.0 · 本地策划工作台')
st.caption('文件在运行本应用的服务器上临时处理：本地启动时在本机，云端部署时会上传到云服务器。无模型调用。所有结果均待审核。')
st.info('公开演示请仅使用虚构或已脱敏资料；敏感项目请使用本地版本。')
st.warning('只导入可信文件，单文件限 300 MB。扫描 PDF 需先 OCR；Word 页眉、文本框和嵌套表格未覆盖；Excel 公式保留原式，不计算。')
a,b=st.columns(2)
projects=a.file_uploader('项目资料（可多选）',type=['pdf','docx','xlsx','txt','md'],accept_multiple_files=True)
experiences=b.file_uploader('个人经验 / 已核实政策与案例（可多选）',type=['pdf','docx','xlsx','txt','md'],accept_multiple_files=True)
query=st.text_input('经验检索关键词', '社区 改造 运营')

def parse(files):
    passages=[]
    with tempfile.TemporaryDirectory(prefix='planning-') as folder:
        for i,f in enumerate(files):
            try:
                path=Path(folder)/f'{i}_{Path(f.name).name}'
                if f.size>300*1024*1024:
                    raise ValueError('文件超过 300 MB')
                f.seek(0)
                with path.open('wb') as target:
                    shutil.copyfileobj(f, target, length=1024*1024)
                with st.spinner(f'正在读取 {i+1}/{len(files)}：{f.name}，大文件可能需要较长时间…'):
                    chunks=read_document(path)
                for p in chunks:
                    p.source=f.name
                passages.extend(chunks)
            except Exception as e:
                st.error(f'{f.name} 读取失败：{e}')
    return passages

def parse_once(files, category):
    signature=tuple((f.name, hashlib.sha256(f.getbuffer()).hexdigest()) for f in files)
    key='parsed_'+category
    previous=st.session_state.get(key)
    if previous is None or previous[0] != signature:
        st.session_state[key]=(signature, parse(files))
    return st.session_state[key][1]

# Session-only results: no cross-user cache or persistent storage.
if not projects:
    st.session_state.pop('parsed_project', None)
if not experiences:
    st.session_state.pop('parsed_experience', None)

if projects:
    project=parse_once(projects, 'project')
    experience=parse_once(experiences, 'experience')
    st.subheader('事实候选与出处')
    st.dataframe(facts(project), use_container_width=True)
    with st.expander('完整提取文本（核查遗漏）'):
        st.json([vars(p) for p in project])
    draft=report(project,experience,query)
    st.text_area('策划草稿（可修改）',draft,height=400,key='draft_'+str(hash(draft)))
    st.download_button('下载未审核草稿', st.session_state['draft_'+str(hash(draft))], '策划初稿_待审核.md')

st.subheader('公开信息搜索（人工选择资料）')
st.caption('点击链接后，仅下方关键词发送到 Bing。不要输入客户名称、地址、内部投资额等敏感信息。搜索结果不是已核实依据。')
public_query=st.text_input('公开检索词（独立于项目文本）','城市更新')
for label,suffix in [('政策',' 政策 site:gov.cn'),('案例',' 案例 运营'),('公开数据',' 统计公报 site:gov.cn')]:
    st.link_button('搜索'+label,'https://www.bing.com/search?q='+quote_plus(public_query+suffix))
st.info('将选定来源下载后导入；另建 TXT 记录：标题、原始网址、发布机关、发布日期、访问日期、适用地区、有效性核验结果。')
