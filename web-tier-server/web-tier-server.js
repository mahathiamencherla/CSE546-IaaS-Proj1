import dotenv from 'dotenv';
import express from 'express';
import AWS from 'aws-sdk';
import cors from 'cors';
import fileupload from "express-fileupload";
import { v4 as uuidv4 } from 'uuid';
import { Consumer } from 'sqs-consumer';

dotenv.config({path: '../key.env'})
const app = express()
// dotenv.config()

app.use(cors({
    origin: '*'
}));
app.use(fileupload());

// map [uniqueID, classification_result]
const map = new Map();

AWS.config.update({region: 'us-east-1'});

const s3 = new AWS.S3({
    accessKeyId: process.env.AWS_KEY,
    secretAccessKey: process.env.AWS_SECRET
})

var Message = function(id, name) {
    this.id = id;
    this.name = name;
}

const SQS = new AWS.SQS({apiVersion: '2012-11-05',accessKeyId: process.env.AWS_KEY,
    secretAccessKey: process.env.AWS_SECRET})
    
const sqsApp = Consumer.create({
    queueUrl: 'https://sqs.us-east-1.amazonaws.com/158146116237/ResponseQueue',
    handleMessage: async (data) => {
        var message = JSON.parse(data.Body)
        console.log("Message received: " + message.id)
        map.set(message.id, message.classification)
    },
    sqs: SQS,
    AttributeNames: [
        "SentTimestamp"
    ],
    MaxNumberOfMessages: 1,
    MessageAttributeNames: [
        "All"
    ],
    VisibilityTimeout: 20,
    WaitTimeSeconds: 10
    });
sqsApp.start();

app.post('/api/image', async(req, res) => {
    // unique ID for the image
    var id = uuidv4();
    //upload image to S3
    let inputBucketKey = Date.now().toString() + req.files.myfile.name;
    const params = {
        Bucket: "input-bucket-images-cc",
        Key: inputBucketKey,
        Body: req.files.myfile.data
    }

    await s3.upload(params).promise()
    console.log("Image Uploaded to S3! for " + inputBucketKey);
    
    // sending request to SQS
    const message = {
        DelaySeconds: 0,
        MessageBody: JSON.stringify(new Message(id, inputBucketKey)),
        QueueUrl: 'https://sqs.us-east-1.amazonaws.com/158146116237/RequestQueue'
    };

    await SQS.sendMessage(message).promise()
    console.log("Message sent to SQS for " + inputBucketKey);
    
    map.set(id,"");
    
    await waitUntilKeyPresent(id, 0)

    //sending result 
    res.send(map.get(id))
})

const snooze = ms => new Promise(resolve => setTimeout(resolve, ms));

const waitUntilKeyPresent = async(key, retryCount) => {
    while (map.get(key) == "" && retryCount < 420) {
        retryCount++;
        await snooze(1000);
    }
    console.log('key present: ' + key)
}

app.listen(3001, () => {
    console.log(`Server running on 3001`)
})
