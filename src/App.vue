<template>
  <div class="common-layout">
    <el-container>
      <el-header style="background-color: #FAFAFA;">
        <el-text class="title" tag="b" size="large">音视频转文字</el-text>

      </el-header>



          <el-main >

            <el-upload
                class="upload-demo"
                drag
                multiple
                :action="uploadUrl" 
                :on-success="handleSuccess" 
              >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                  只能上传mp3/mp4文件，且不超过10mb
              </div>
            </template>
          </el-upload>

          <!-- <div>
            <input type="file" ref="fileInput" @change="uploadFile" />
            <button @click="submitFile">上传文件</button>
          </div> -->



        <el-input
          style="margin-top: 15px;"
          v-model="oneBestText"
          :autosize="{ minRows: 1, maxRows: 10 }"
          type="textarea"
          placeholder="转换结果"
        />


          </el-main>



    </el-container>
  </div>
</template>

<script>
import axios from 'axios';
import { UploadFilled } from '@element-plus/icons-vue';
export default {
  data() {
      return {
        // selectedFile: null,
        uploadUrl:'http://127.0.0.1:5000/process',
        oneBestText: '', // 用于存储 onebest 数据的变量
      };
    },
  methods: {

    // uploadFile(event) {
    //   this.selectedFile = event.target.files[0];
    // },
    // async submitFile() {
    //   if (!this.selectedFile) {
    //     // 确保已选择文件
    //     return;
    //   }

    //   const formData = new FormData();
    //   formData.append('file', this.selectedFile);

    //   try {
    //     const response = await axios.post('http://127.0.0.1:5000/process', formData, {
    //       headers: {
    //         'Content-Type': 'multipart/form-data',
    //       },
    //     });

    //     // 处理上传成功的响应
    //     console.log('文件上传成功：', response.data);
    //   } catch (error) {
    //     // 处理上传失败
    //     console.error('文件上传失败1：', error);
    //   }
    // },
    // async uploadFile(event) {
    //   console.log(1);
    //   const file = event.target.files[0];

    //   if (file) {
    //     const formData = new FormData();
    //     formData.append('file', file);

    //     try {
    //       const response = await axios.post('http://127.0.0.1:5000/process', formData, {
    //         headers: {
    //           'Content-Type': 'multipart/form-data',
    //         },
    //       });

    //       // 处理服务器的响应
    //       console.log('文件上传成功：', response.data);
    //     } catch (error) {
    //       // 处理上传失败
    //       console.error('文件上传失败2：', error);
    //     }
    //   }
    // },
    handleSuccess(response, file) {
      // 处理文件上传成功后的回调
      console.log('上传成功', response);
      // 提取 onebest 的信息
      const responseData = JSON.parse(response.data);
      if (responseData && responseData.length > 0) {
      // 提取 onebest 的信息
      const oneBestArray = responseData.map(item => item.onebest);
      
      // 将多个 onebest 合并为一个字符串
      this.oneBestText = oneBestArray.join(' ');
      
      }
    },
  },
};
</script>

<style>

.title{
    display: flex;
    justify-content: center; /* 水平居中 */
    align-items: center; /* 垂直居中 */
    margin-top: 20px;
    margin-bottom: 20px;

}

</style>
