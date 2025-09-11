Auto-recognition of Evidentials [![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://autorecognition-sdcmrsmudbn8g2xxg266mr.streamlit.app/)


	A simple and interactive web app built with Streamlit, designed to demonstrate how evidentials can be explored through local grammar analysis and fine-tuned language models.
 
Features
	
	Interactive Data Visualization
	Explore the distribution of English reporting verbs and their local grammatical patterns.
	
	AI-Powered Analysis
	Combines rule-based and deep learning approaches to achieve precise identification and annotation of reporting verbs in discourse.
	
	Fast Deployment with Streamlit
	Deploy locally or on the cloud within minutes.
	
	🛠Research-Oriented Workflow
	Provides a reproducible framework for the quantitative study of evidentiality in news and academic discourse.

Installation

	Clone the repository and install dependencies:
	
	git clone [https://github.com/PseudoInsider/autoRecognition.git]
	cd the position you download the file
	pip install -r requirements.txt


Running the App
	
	Start the app locally:
	
	streamlit run app.py
	
	Then open your browser at http://localhost:8501.

Project Structure

	.
	├── app.py              # Main Streamlit app
	├── requirements.txt    # Dependencies
	├── data/               # (Optional) Dataset folder
	└── README.md           # Documentation


Deployment

	You can deploy the app easily with:
	
	Streamlit Community Cloud
	
	Heroku
	
	Render
	
	Example for Streamlit Cloud:
	
	Push your code to GitHub
	
	Sign in at share.streamlit.io
	
	Deploy your repo and select app.py

Research Background

	This app is part of a study addressing the methodological gap in local grammar analysis of evidentiality. Existing research often lacks objective, quantitative tools, limiting discourse-functional insights.
	
	To overcome this, our approach integrates:
	
	Local grammar & construction grammar frameworks
	
	Fine-tuned language models for automatic recognition of reporting verbs
	
	Hybrid rule-based + deep learning methods for accurate functional annotation
	
	Results: The model achieves an overall F1 score of 90.78%, demonstrating both accuracy and stability.
	
	This work deepens the cognitive analysis of evidentiality in knowledge discourse, proposes an expandable quantitative framework, and contributes to improving precision in local grammar analysis and research on information dissemination.

Contributing

	We welcome contributions!
	
	Fork the repo
	
	Create a feature branch
	
	Submit a Pull Request

License

	This project is licensed under the MIT License.
 	If you use this app or the underlying methods in your research, please cite our work:
  		Huan, C., & Wang, L. (forthcoming). The application of language model fine-tuning techniques to local grammar: Automated recognition of evidentials. Foreign Languages and their Teaching. 
		Huan, C., & Wang, L., 2025. Discourse Communication Effectiveness Evaluation System for Information Source. Github. Available at https://github.com/PseudoInsider/autoRecognition.git
