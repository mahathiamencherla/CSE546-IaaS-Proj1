import dotenv from 'dotenv'
import express from 'express'
import multer from 'multer'
import AWS from 'aws-sdk'
import cors from 'cors'
dotenv.config({path: '../key.env'})
const app = express()
const port = 3000
dotenv.config()

app.use(cors({
    origin: '*'
}));

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

const upload = multer({storage}).single('image')

AWS.config.update({region: 'us-east-1'})

const SQS = new AWS.SQS({apiVersion: '2012-11-05',accessKeyId: process.env.AWS_KEY,
    secretAccessKey: process.env.AWS_SECRET})

app.post('/api/image',upload,(req, res) => {

    const params = {
        Bucket: "iaas-proj-input",
        Key: req.file.originalname,
        Body: req.file.buffer
    }

    s3.upload(params, (error, data) => {
        if(error){
            res.status(500).send(error)
        }
        res.status(200).send(data)
    })

    const message = {
        DelaySeconds: 10,
        MessageBody: req.file.originalname,
        QueueUrl: "https://sqs.us-east-1.amazonaws.com/676148463056/RequestQueue"
    };
    SQS.sendMessage(message, (err,result) => {
        if (err) {
            console.log(err)
            return
        }
        console.log(result)
    })
})

app.listen(3001, () => {
    console.log(`Server running on 3001`)
})