# Welcome to the second version of the Stock Tool.

This project was initially created for a class project for Software Engineering at the University of Wisconsin-Whitewater
The members of this project included: Brian Shuler, Haki Dehari, Isaiah Morales, as well as myself.

Haki Dehari created a tool that collected Twitter/Reddit posts and generated sentiment scores for specific stocks based off of the posts.
Brian Shuler created a MySQL database that stored the Twitter posts and sentiment scores.
Isaiah Morales and I worked on the front-end, which displayed stock price history and sentiment scores for given stocks.

After that project ended, I decided upon expanding upon the Stock Tool as my capstone project for my masters degree.
While a solid portion of the code could be salvaged for the second iteration of the Stock Tool, a much different process is used.

My second project revolving around the Stock Tool was a Machine Learning final project. This project was completed by Brian Shuler and I
The purpose of this project was to find a correlation between sentiment scores and stock price: results were suboptimal.

In the process of completing this project, a new data collection algorithm was created from scratch. 
A listener ran 24/7 on my laptop to listen for Tweets, and a sentiment service created sentiment scores at the end of each day.
These files were saved as CSVs on my laptop for 4 months.

Eventually, I was close enough to my capstone deadline to utilize the Google Cloud Platform's 90-day $300 free credit.
Now the Twitter Listener and sentiment Service run off of the Google Cloud Platform.

The UI could be mostly salvaged, with the exception of displaying the sentiment scores (as the data structure of sentiment data changed in the process).
The UI will eventually be hosted off of the Google Cloud Platform as well.
