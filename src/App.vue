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
                action="https://run.mocky.io/v3/9d059bf9-4660-45f2-925d-ce80ad6c4d15"
                multiple>
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



          </el-main>



    </el-container>
  </div>
</template>
<script setup lang="ts">
import { UploadFilled } from '@element-plus/icons-vue'
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
