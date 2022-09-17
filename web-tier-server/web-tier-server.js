import dotenv from 'dotenv'
import express from 'express'
import multer from 'multer'
import AWS from 'aws-sdk'
import cors from 'cors'
import bodyParser from 'body-parser'
import fileupload from "express-fileupload"
import { v4 as uuidv4 } from 'uuid';
import { Consumer } from 'sqs-consumer';

dotenv.config({path: '../key.env'})
const app = express()
dotenv.config()

app.use(cors({
    origin: '*'
}));
app.use(fileupload());

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

var Message = function(id, name) {
    this.id = id;
    this.name = name;
}

// const upload = multer({storage}).single('image')
var upload = multer({ dest: 'uploads/' })

AWS.config.update({region: 'us-east-1'})

const SQS = new AWS.SQS({apiVersion: '2012-11-05',accessKeyId: process.env.AWS_KEY,
    secretAccessKey: process.env.AWS_SECRET})

var SQSparams = {
    QueueUrl: 'https://sqs.us-east-1.amazonaws.com/676148463056/ResponseQueue',
    AttributeNames: [
        "SentTimestamp"
    ],
    MaxNumberOfMessages: 1,
    MessageAttributeNames: [
        "All"
    ],
    VisibilityTimeout: 20,
    WaitTimeSeconds: 10
    };
    
const sqsApp = Consumer.create({
    queueUrl: 'https://sqs.us-east-1.amazonaws.com/676148463056/ResponseQueue',
    handleMessage: async (data) => {
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

app.post('/api/image',(req, res) => {
    const params = {
        Bucket: "iaas-proj-input",
        Key: req.files.myfile.name,
        Body: req.files.myfile.data
    }

    s3.upload(params, (error, data) => {
        // if(error){
        //     res.status(500).send(error)
        // }
        // res.status(200).send(data)
    })

    var id = uuidv4();
    
    console.log(JSON.stringify(new Message(id, req.files.myfile.name)))
    const message = {
        DelaySeconds: 0,
        MessageBody: JSON.stringify(new Message(id, req.files.myfile.name)),
        QueueUrl: "https://sqs.us-east-1.amazonaws.com/676148463056/RequestQueue"
    };
    SQS.sendMessage(message, (err,result) => {
        if (err) {
            console.log(err)
            return
        }
    })

    // TODO: Response part
    map.set(id,"")
    console.log('Sent message for ' + req.files.myfile.name)
    waitUntilKeyPresent(id)
    res.send(map.get(id))
    // console.log(map.get(id))

    // var result = ReceiveMessage(id)
    // console.log(result)
    // var result = ""
    // while (true) {
    //     console.log('in while')
    //     result = ReceiveMessage(id)
    //     console.log(result)
    // }
    
})

function waitUntilKeyPresent(key) {
    if (map.get(key) == "") {
        console.log('key not present')
        setTimeout(waitUntilKeyPresent, 10000, key);
    } else {
        console.log('key present: ' + key)
        console.log(map.get(key))
        return
    }
}

// function ReceiveMessage(id) {
//     SQS.receiveMessage(SQSparams, function(err, data) {
//         console.log('Searching for message')
//         console.log(data)
//         if (err) {
//           console.log("Receive Error", err);
//         } else if (data.Messages) {
//             var message = JSON.parse(data.Messages[0].Body)
//             console.log(message.image)
//             if (message.id == id) {
//                 var deleteParams = {
//                     QueueUrl: 'https://sqs.us-east-1.amazonaws.com/676148463056/ResponseQueue',
//                     ReceiptHandle: data.Messages[0].ReceiptHandle
//                 };
//                 SQS.deleteMessage(deleteParams, function(err, data) {
//                     if (err) {
//                         console.log("Delete Error", err);
//                     } else {
//                         console.log("Message Deleted", data);
//                     }
//                 });
//                 console.log('Received classification for ' + message.image)
//                 return message.classification
//             }
//         }
//     });
// }

app.listen(3001, () => {
    console.log(`Server running on 3001`)
})