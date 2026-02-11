
content = """requests
beautifulsoup4
pandas
numpy
scikit-learn
google-generativeai
matplotlib
networkx
python-dotenv
streamlit>=1.42.0
plotly
seaborn
apscheduler
pillow
tzdata
altair<5
"""

with open('requirements.txt', 'w', encoding='utf-8') as f:
    f.write(content)

print("requirements.txt has been rewritten with UTF-8 encoding and pinned versions.")
