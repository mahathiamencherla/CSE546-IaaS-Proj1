require('dotenv').config({ path:'key.env' });

const express = require('express')
const multer = require('multer')
const AWS = require('aws-sdk')
const cors = require('cors');
const app = express()
const port = 3000

app.use(cors({
    origin: '*'
}));

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

app.post('/api/image',upload,(req, res) => {

    let myFile = req.file.originalname.split(".")

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
})

app.listen(3000, () => {
    console.log(`Server running on 3000`)
})