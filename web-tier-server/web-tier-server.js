import dotenv from 'dotenv';
import express from 'express';
import multer from 'multer';
import AWS from 'aws-sdk';
import cors from 'cors';
// import bodyParser from 'body-parser'
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

const storage = multer.memoryStorage({
    destination: function(req, file, callback) {
        callback(null, '')
    }
})

var Message = function (id, name) {
    this.id = id;
    this.name = name;
}

// const upload = multer({storage}).single('image')
var upload = multer({ dest: 'uploads/' })

AWS.config.update({region: 'us-east-1'})

const SQS = new AWS.SQS({apiVersion: '2012-11-05',accessKeyId: process.env.AWS_KEY,
    secretAccessKey: process.env.AWS_SECRET})
    
const sqsApp = Consumer.create({
    queueUrl: 'https://sqs.us-east-1.amazonaws.com/676148463056/ResponseQueue',
    handleMessage: async (data) => {
        console.log("Message received")
        var message = JSON.parse(data.Body)
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
    console.log("in post req")
    //upload image to S3
    let inputBucketKey = Date.now().toString() + req.files.myfile.name;
    console.log("input: ", inputBucketKey);
    const params = {
        Bucket: "iaas-proj-input",
        Key: inputBucketKey,
        Body: req.files.myfile.data
    }

    s3.upload(params, (error, data) => {
        if(error){
            console.log("Error in uploading image to S3: ", error);
        } else {
            console.log("Image Uploaded to S3!");
        }
    })
    
    // sending request to SQS
    const message = {
        DelaySeconds: 0,
        MessageBody: JSON.stringify(new Message(id, inputBucketKey)),
        QueueUrl: "https://sqs.us-east-1.amazonaws.com/676148463056/RequestQueue"
    };

    SQS.sendMessage(message, (err,result) => {
        if (err) {
            console.log(err)
            return
        }
    })

    
    map.set(id,"");

    console.log('Sent message for ' + inputBucketKey);
    
    await waitUntilKeyPresent(id, 0)

    //sending result 
    res.send(map.get(id))
})

const snooze = ms => new Promise(resolve => setTimeout(resolve, ms));

const waitUntilKeyPresent = async(key, retryCount) => {
    while (map.get(key) == "" && retryCount < 420) {
        retryCount++;
        console.log('key not present')
        await snooze(1000);
    }
    console.log('key present: ' + map.get(key))
}

app.listen(3001, () => {
    console.log(`Server running on 3001`)
})