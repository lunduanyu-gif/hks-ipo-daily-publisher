import os
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

from dotenv import load_dotenv
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, '.env'))

sys.argv = ['',
    '--title', '创新药行业报告2026',
    '--desc', '2026年全球创新药5大趋势：AI融合、并购加速、中国崛起、政策红利、技术前沿。一场不可逆的行业升级正在发生',
    '--images',
    r'C:\Users\77961\.openclaw\workspace-cmo\post-to-wechat\2026-03-22\xhs-cover.png',
    r'C:\Users\77961\.openclaw\workspace-cmo\post-to-wechat\2026-03-22\xhs-1.png',
    r'C:\Users\77961\.openclaw\workspace-cmo\post-to-wechat\2026-03-22\xhs-2.png',
    r'C:\Users\77961\.openclaw\workspace-cmo\post-to-wechat\2026-03-22\xhs-3.png',
    r'C:\Users\77961\.openclaw\workspace-cmo\post-to-wechat\2026-03-22\xhs-4.png',
    r'C:\Users\77961\.openclaw\workspace-cmo\post-to-wechat\2026-03-22\xhs-5.png',
    '--tags', '创新药,行业分析,AI医药,生物医药,IPO投资,港股打新,医疗投资,财经'
]

from publish_xhs import main
main()
