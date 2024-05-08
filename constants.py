QUERY = """
    fields @timestamp, @message, @logStream, @log
    | sort @timestamp desc
    | limit 100
    """
    
LOG_GROUP = """/codebuild/awslearning/aws_watermark"""
