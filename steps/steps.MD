The following steps outline my train of thought and actions taken to materialize this data engineering project. Each step reflects the challenges, solutions, and decisions I navigated throughout the development process. From the initial idea to its implementation, these steps detail my approach towards achieving the successful realization of the project.

# Step 1: The Idea
It all began with the idea of creating a data engineering project to showcase my skills, particularly in AWS and Python, as these are the areas where I have professional expertise. Being a huge fan of the K-Pop group TWICE, I decided to center the project around them.

My initial focus was on obtaining metadata from TWICE's music videos on YouTube. The goal was to visualize the growth of various metrics over time, like views, likes, and comments. Ultimately, my goal was to lay the groundwork for potential future endeavors. While I didn't plan to personally develop a predictive model, my aim was to set up the foundation so that a data science team could potentially work on such a predictive model in the future, similar to real-world scenarios tackled by companies.

Starting out, I was unsure how to gather this metadata. After some research, I discovered the potential of the Google Cloud Console. Creating a project in my account and utilizing the 'YouTube Data API v3' became the first step. Reading through the API documentation and understanding its integration with Python, I managed to create a simple script that fetched the view count of a YouTube video.

During this phase, I encountered challenges in retrieving other data such as likes or dislikes. I realized certain channels restricted access to their like counts, requiring special consideration in the Python script. I addressed this by implementing a 'try-except' logic to handle such cases.

I decided to use Python threads to simulate a professional environment where this technique is commonly used to process a large amount of data.

Once I had a fully functional Python script capable of retrieving various data such as likes, comments, views, and the video's publication date, I contemplated how to model the data for subsequent visualization in Tableau. Given the data's structure, I opted for the simplest approach: storing it in a table within a database. Click here to see the [code of the Python script](../script/youtube_script.py).

Having figured out the data extraction and structured the data table, the remaining puzzle was how to execute the script within AWS and where to store the information.

# Step 2: Using AWS Free Tier
While I'm familiar with AWS Redshift, its usage isn't part of the free tier (except for a 2-month free trial). To exhibit experience with various AWS services, I pondered two potential solutions:
1. Storing data in S3 in JSON or Parquet format, considering real-world scenarios where data often requires a well-compressed format.
2. Storing data in RDS.

After researching, I found that although Tableau is working on integrating a connector with AWS S3, it's still in the beta phase. Therefore, I had to opt for solely storing the data in RDS.
For additional information on Tableau and Amazon S3 integration, you can refer to the [Tableau documentation here](https://help.tableau.com/current/pro/desktop/es-es/examples_amazons3.htm).

Now that I had decided to use RDS and PostgreSQL after consulting the documentation at [AWS repost](https://repost.aws/knowledge-center/free-tier-rds-launch), the next consideration was which AWS service would execute the Python script. Note: Is important to configure the RDS to be to be publicly accessible not private.

## Failure 1: AWS Lambda
Given that the script was relatively straightforward, Lambda seemed the simplest option. However, using Lambda required creating a Lambda layer with necessary libraries. While some libraries like pandas are simple and even come with a default Lambda layer, integrating the 'google-api-python-client' library proved more challenging.

To create this layer, I leveraged Docker to ensure the script functioned seamlessly outside of my local environment, with only the essentials needed for execution. Despite successfully creating the layer, attempting to execute the script in Lambda resulted in compatibility errors and missing dependencies.

After extensive research on forums, I was unable to find a resolution for these issues.

After the unsuccessful attempt with Lambda, I considered utilizing an EC2 instance, as it also falls within the AWS Free Tier.

## Step 3: EC2
Following the official tutorials provided by AWS at [AWS EC2 User Guide](https://docs.aws.amazon.com/es_es/AWSEC2/latest/UserGuide/tutorial-connect-ec2-instance-to-rds-database.html), I successfully set up a free-tier EC2 instance and established a proper connection with RDS. However, during this process, I discovered a potential cost implication within the tutorial. It did not specify that the RDS and EC2 should be in the same availability zone to prevent incurring additional costs

I opted for an Amazon-suggested EC2 instance with the Amazon Linux 2023 OS image. However, I had to acquaint myself with some basic Linux commands. For instance, when installing PostgreSQL, I learned that on this system, one can't use 'yum' or 'apt'. Instead, the command 'dnf' is utilized. To install PostgreSQL, I used the commands:

```bash
sudo dnf install postgresql15.x86_64 postgresql15-server

```
Additionally, I had to install other dependencies such as:

```bash
sudo dnf install python3-devel
sudo dnf install libpq-devel
```

These commands were essential to ensure the proper installation of PostgreSQL and its related dependencies on the Amazon Linux 2023 instance.

See more details at [How to Install PostgreSQL 15 Amazon Linux](https://linux.how2shout.com/how-to-install-postgresql-15-amazon-linux-2023/)

During the instance setup, I vaguely recall encountering issues even with the 'sudo' command, which wasn't being recognized. Regrettably, I can't recall the specific solution I used to rectify this at the moment.

Once I successfully installed PostgreSQL and the necessary Python libraries (fortunately, the instance already had Python installed), I delved into some Linux basics to save my Python script there and set it up for execution. The subsequent step involved creating a cronjob to automate the script's daily execution.

However, I encountered difficulties with the 'crontab' command. Installing 'cronie' was one of the solutions that allowed me to view the cron logs. [Installing CronTab on Amazon Linux 2023 EC2](https://jainsaket-1994.medium.com/installing-crontab-on-amazon-linux-2023-ec2-98cf2708b171) Eventually, the functional cron command I used was:

```bash
0 18 * * * root /usr/bin/python3 /home/scripts/youtube_script.py
```

This cron job was set to execute the Python script automatically daily at 6:00 PM. To see the logs you use the command:

```bash
sudo systemctl status crond.service
```

Another aspect I learned was how to interact with PostgreSQL directly from the command line. Throughout my journey, I had mainly used the DBeaver graphical interface, so this was a new experience for me. To access the database from the EC2 instance, the command used was:

```bash
psql -h host -U user -d DatabaseName
```

After entering this command, the console prompted me to input the password. During this interaction, I discovered that you can use various commands such as \d, \dt, \dn, and \q to view tables, schemas, or exit the database. These commands proved to be incredibly useful, simplifying the process of querying common information and navigating within the database.

Finally, with the script running on the EC2 instance, the data was steadily accumulating in the RDS database day by day.

## Step 4: Tableau
The next step was to establish the connection between RDS and Tableau. To do this, I needed to check the settings of the security group or VPC, depending on the AWS VPC configuration. It's crucial to remember that when initially setting up your RDS, you should configure it to be publicly accessible.

Afterward, I created the dashboard showcasing the YouTube data. However, for publishing the dashboard on Tableau Public, I chose to use a CSV file to host it on the site, enabling users to download, modify, or replace the data with that of their favorite artist. Nevertheless, the primary aim was to establish a direct connection with RDS on their local computer.

This marked the completion of the project, culminating in the creation of a dashboard displaying YouTube data in Tableau. The flexibility to either use Tableau Public or set up a direct connection with RDS on a local machine offered versatility in accessing and utilizing the data.
