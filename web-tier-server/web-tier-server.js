import dotenv from 'dotenv'
import express from 'express'
import multer from 'multer'
import AWS from 'aws-sdk'
import cors from 'cors'
import bodyParser from 'body-parser'
import fileupload from "express-fileupload";
dotenv.config({path: '../key.env'})
const app = express()
dotenv.config()

app.use(cors({
    origin: '*'
}));
app.use(fileupload());


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

// const upload = multer({storage}).single('image')
var upload = multer({ dest: 'uploads/' })

AWS.config.update({region: 'us-east-1'})

const SQS = new AWS.SQS({apiVersion: '2012-11-05',accessKeyId: process.env.AWS_KEY,
    secretAccessKey: process.env.AWS_SECRET})

app.post('/api/image',(req, res) => {
    const params = {
        Bucket: "iaas-proj-input",
        Key: req.files.myfile.name,
        Body: req.files.myfile.data
    }

    s3.upload(params, (error, data) => {
        if(error){
            res.status(500).send(error)
        }
        res.status(200).send(data)
    })

    const message = {
        DelaySeconds: 10,
        MessageBody: req.files.myfile.name,
        QueueUrl: "https://sqs.us-east-1.amazonaws.com/676148463056/RequestQueue"
    };
    SQS.sendMessage(message, (err,result) => {
        if (err) {
            console.log(err)
            return
        }
    })
    console.log('Sent message for ' + req.files.myfile.name)
})

app.listen(3001, () => {
    console.log(`Server running on 3001`)
})