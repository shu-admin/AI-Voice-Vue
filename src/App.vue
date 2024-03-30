<template>
  <div class="common-layout">
    <el-container>
      <!-- 左侧导航 -->
      <el-aside width="200px">
        <el-menu
          default-active="1"
          class="aside-menu"
          @select="handleSelect"
        >
          <el-menu-item index="1">语音转文字</el-menu-item>
          <el-menu-item index="2">文字转语音</el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 右侧内容 -->
      <el-container>
        <!-- 标题栏 -->
        <el-header style="background-color: #FAFAFA; text-align: center;">
          <b>{{ currentViewTitle }}</b>
        </el-header>

        <!-- 主内容区 -->
        <el-main>
          <div v-if="currentView === 'audioToText'">
            <!-- 语音转文字的内容 -->
            <el-upload
              class="upload-demo"
              drag
              multiple
              :action="uploadUrl"
              :file-list="fileList"
              :limit="3"
              :on-exceed="handleExceed"
              :on-preview="handlePreview"
              :on-remove="handleRemove"
              :before-remove="beforeRemove"
              :on-success="handleSuccess"
            >
              <i class="el-icon-upload"></i>
              <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
              <div slot="tip" class="el-upload__tip">只能上传mp3/mp4文件，且不超过10mb,最多同时支持上传3个文件。</div>
            </el-upload>
            <el-input
              v-model="oneBestText"
              type="textarea"
              autosize
              placeholder="转换结果"
            />
            <el-button type="primary" @click="exportToTxt">导出为TXT</el-button>
          </div>
          <div v-if="currentView === 'textToSpeech'">
            <!-- 文字转语音的内容 -->
            <el-input
              v-model="textToSpeechInput"
              type="textarea"
              autosize
              placeholder="请输入文本"
            />
            <!-- 音频编码选择 -->
            <el-select v-model="aue" placeholder="请选择音频编码">
                  <el-option
                    v-for="encoding in audioEncodings"
                    :key="encoding.value"
                    :label="encoding.label"
                    :value="encoding.value"
                    :disabled="encoding.disabled">
                  </el-option>
                </el-select>

                <!-- 发音人选择 -->
                <el-select v-model="vcn" placeholder="请选择发音人">
                  <el-option
                    v-for="actor in voiceActors"
                    :key="actor.value"
                    :label="actor.label"
                    :value="actor.value">
                  </el-option>
                </el-select>

            <!-- 语速选择 -->
            <div class="block">
              <span class="demonstration">语速</span>
              <el-slider v-model="speed" :min="0" :max="100" label="语速"></el-slider>
            </div>
            <!-- 音量选择 -->
            <div class="block">
              <span class="demonstration">音量</span>
              <el-slider v-model="volume"  :min="0" :max="100" label="音量"></el-slider>
            </div>
            <!-- 音高选择 -->
            <div class="block">
              <span class="demonstration">音高</span>
              <el-slider v-model="pitch" :min="0" :max="100" label="音高"></el-slider>
            </div>
            <el-button @click="convertTextToSpeech">转换为语音</el-button>
                <!-- 成功时显示音频播放器和下载按钮 -->
                <div v-if="audioUrl" class="audio-container">
                  <el-row type="flex" align="middle" class="audio-row">
                    <el-col :span="2">
                      <el-icon class="audio-icon" :size="40">
                        <i class="el-icon-headset"></i>
                      </el-icon>
                    </el-col>
                    <el-col :span="16">
                      <div class="audio-description">
                        语音合成成功，点击播放或下载
                      </div>
                      <audio :src="audioUrl" controls class="audio-player"></audio>
                    </el-col>
                    <el-col :span="6" class="audio-download">
                      <a :href="audioUrl" download="audio.mp3">
                        <el-button type="success" icon="el-icon-download">下载音频</el-button>
                      </a>
                    </el-col>
                  </el-row>
                </div>

            <!-- 出现错误时显示错误信息 -->
            <div v-if="showError">
              <p>音频转换失败，请稍后重试。</p>
            </div>
          </div>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
export default {
  data() {
    return {
      audioUrl: '', // 用于存储音频文件的URL
      showError: false, // 是否显示错误信息
      aue: 'lame',
      textToSpeechInput: '',
      audioEncodings: [
        { value: 'raw', label: '未压缩的pcm' ,disabled: true},
        { value: 'lame', label: 'mp3' },
        { value: 'speex-org-wb;7', label: '开源speex（16k）',disabled: true },
        { value: 'speex-org-nb;7', label: '开源speex（8k）' ,disabled: true},
        { value: 'speex;7', label: '定制speex（8k）',disabled: true },
        { value: 'speex-wb;7', label: '定制speex（16k）',disabled: true }
      ],
      vcn: '',
      voiceActors: [
        { value: 'x4_lingxiaoyao_em', label: '情感女声' },
        { value: 'x2_xiaofei', label: '合肥男声' },
        { value: 'x4_enus_gavin_assist', label: '英语男声' },
        { value: 'x2_xiaoqiang', label: '湖南男声' },
        { value: 'x_yuer', label: '台普女声' },
        { value: 'x2_xiaoying', label: '陕西女声' },
        { value: 'x4_EnUs_Lindsay_assist', label: '英语女声' },
        { value: 'qianhui', label: '日语女声' },
        { value: 'x3_xiaodu', label: '成都女声' },
        { value: 'x4_lingfeizhe_zl', label: '普通话男声' }
      ],
      speed: 50,
      volume: 50,
      pitch: 50,
      fileList: [],
      currentView: 'audioToText', // 当前视图
      currentViewTitle: '语音转文字', // 当前视图的标题
      uploadUrl: 'https://cryptic-stream-41825-70b422ac31aa.herokuapp.com/process',
      oneBestText: '',
      textToSpeechInput: '',
    };
  },
  methods: {

    handleRemove(file, fileList) {
        console.log(file, fileList);
    },
    handlePreview(file) {
        console.log(file);
    },
    handleExceed(files, fileList) {
        this.$message.warning(`当前限制选择 3 个文件，本次选择了 ${files.length} 个文件，共选择了 ${files.length + fileList.length} 个文件`);
    },
    beforeRemove(file, fileList) {
        return this.$confirm(`确定移除 ${ file.name }？`);
    },

    handleSuccess(response, file) {
      //将文件名增加到列表中
      this.fileList.push(file.name);
      // 文件上传成功的处理逻辑
      // 处理文件上传成功后的回调
      console.log('上传成功', response);
      // 提取 onebest 的信息
      const responseData = JSON.parse(response.data);
      if (responseData && responseData.length > 0) {
      // 提取 onebest 的信息
      const oneBestArray = responseData.map(item => item.onebest);
      console.log('文件名', file.name);
      console.log('文件识别结果', oneBestArray);
      // 将多个 onebest 合并为一个字符串
      this.oneBestText += (this.oneBestText ? '\n\n' : '') + '文件' + file.name + '的识别结果：\n' + oneBestArray.join(' ');
      }
    },
    exportToTxt() {
    if (!this.oneBestText) {
      alert('没有可导出的内容！');
      return;
    }
    const blob = new Blob([this.oneBestText], { type: 'text/plain;charset=utf-8' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = '转换文本.txt';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  },
    convertTextToSpeech() {
      // 文字转语音的处理逻辑
      this.audioUrl = ''; // 清除之前的音频URL
      // 构建请求体，确保与后端接收的格式一致
      const requestBody = {
            text: this.textToSpeechInput, // 文字内容
            aue: this.aue, // 音频编码
            vcn: this.vcn, // 发音人
            speed: this.speed, // 语速
            volume: this.volume, // 音量
            pitch: this.pitch, // 音高
          };

          // 使用axios发送POST请求到后端
          this.$axios.post('https://cryptic-stream-41825-70b422ac31aa.herokuapp.com/text2speech', requestBody)
            .then(response => {
              // 这里处理后端的响应
              console.log('转换成功', response);
              // 假设后端返回的response中包含音频文件的URL
              this.audioUrl = "https://cryptic-stream-41825-70b422ac31aa.herokuapp.com/audio/demo.mp3"; // 更新audioUrl状态
              this.showError = false; // 成功获取音频后不显示错误信息
              // 例如，如果后端返回音频文件的URL，可以在这里处理
            })
            .catch(error => {
              console.error('转换失败', error);
              this.showError = true; // 出现错误时显示错误信息
              this.audioUrl = ''; // 清除之前的音频URL
            });
    },
    handleSelect(key, keyPath) {
      if (key === '1') {
        this.currentView = 'audioToText';
        this.currentViewTitle = '语音转文字';
      } else if (key === '2') {
        this.currentView = 'textToSpeech';
        this.currentViewTitle = '文字转语音';
      }
    },
  },
};
</script>

<style>
/* 左侧导航样式调整，采用更柔和的色彩 */
.aside-menu {
  height: 100%;
  background-color: #F9FAFB; /* 浅灰色背景 */
  color: #606266; /* 深灰色文字 */
}

/* 菜单项悬浮和选中状态 */
.el-menu-item:focus, .el-menu-item:hover, .el-menu-item.is-active {
  background-color: #EFEFEF; /* 浅灰色背景 */
}

/* 上传组件和按钮的样式调整，以及文本框 */
.upload-demo, .el-button, .el-input__inner {
  border: 1px solid #DCDFE6; /* 浅灰色边框 */
  border-radius: 4px; /* 轻微的圆角 */
}

/* 上传提示文字样式 */
.el-upload__text {
  color: #606266; /* 深灰色 */
}

/* 按钮颜色调整 */
.el-button {
  background-color: #409EFF; /* 蓝色背景 */
  color: white; /* 白色文字 */
  border: none; /* 移除边框 */
}

/* 标题栏样式，更简约 */
.el-header {
  background-color: #F9FAFB; /* 浅灰色背景 */
  color: #303133; /* 深灰色文字 */
}

/* 主体内容背景调整，更为清晰 */
.el-main {
  background-color: #FFFFFF; /* 白色背景 */
  margin: 16px; /* 外边距，增加一些空间 */
  padding: 20px; /* 内边距，增加内容区的空间 */
  border: 1px solid #DCDFE6; /* 细边框 */
}

/* 总体布局的微调 */
.common-layout {
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06); /* 轻微的阴影效果 */
  border-radius: 4px; /* 整体圆角 */
}



/* 调整上传组件的间距 */
.upload-demo {
  margin-bottom: 20px; /* 与下一个组件之间增加间距 */
}

/* 输入框和按钮的上下边距调整 */
.el-input, .el-button {
  margin-top: 20px; /* 增加顶部间距 */
  margin-bottom: 20px; /* 增加底部间距，适用于下方还有其他元素的情况 */
}

/* 主内容区的上下边距调整 */
.el-main {
  padding-top: 30px; /* 内部顶部填充增加，使内容不紧贴标题栏 */
  padding-bottom: 30px; /* 内部底部填充增加，为底部内容与容器边缘增加空间 */
}

/* 调整标题栏的上下内边距，使标题更加突出 */
.el-header {
  padding-top: 20px; /* 增加顶部内边距 */
  padding-bottom: 20px; /* 增加底部内边距 */
}

/* 如果有特定的容器或部分需要更多间距，可以单独调整 */
.custom-section {
  margin-top: 30px; /* 举例：为自定义部分增加顶部外边距 */
  margin-bottom: 30px; /* 举例：为自定义部分增加底部外边距 */
}

/* 设置html和body高度为100% */
html, body {
  height: 100%;
  margin: 0; /* 移除默认边距 */
}

/* 设置Vue组件最外层容器的高度 */
.common-layout {
  display: flex; /* 使用Flex布局 */
  flex-direction: column; /* 子元素垂直排列 */
  height: 100%; /* 撑满整个视口的高度 */
}

/* 设置Element Plus容器元素以填充全屏 */
.el-container {
  flex: 1; /* 填充剩余空间，确保撑满整个父容器 */
  display: flex; /* 再次声明，以便内部元素也能使用Flex布局 */
  flex-direction: row; /* 默认为行排列，侧边栏和内容并排 */
}

/* 针对侧边栏和内容的高度设置 */
.el-aside, .el-main {
  height: 100%; /* 确保这些部分也会撑满高度 */
}

.el-aside {
  flex-shrink: 0; /* 防止侧边栏被压缩 */
}

.el-main {
  flex: 1; /* 主内容区占据剩余空间 */
}

/* 下拉选择框和输入框的统一样式 */
.el-select, .el-input {
  margin-bottom: 15px; /* 元素间距 */
  width: 65%; /* 宽度调整为80% */
}

/* 滑动条样式 */
.el-slider {
  width: 40%; /* 宽度调整为80% */
  margin-bottom: 20px; /* 元素间距 */
}

/* 定制化滑动条内部样式 */
.el-slider__bar {
  background-color: #409EFF; /* 蓝色主题 */
}

/* 发音人输入框特定样式 */
.el-input__inner {
  border-color: #f5f5f6; /* 边框颜色 */
  border-radius: 20px; /* 圆角 */
}

/* 发音人输入框聚焦时的样式 */
.el-input__inner:focus {
  border-color: #fcfefb; /* 绿色高亮 */
}

.audio-container {
  margin: 20px 0;
  padding: 15px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
  border-radius: 8px;
  background-color: #f9f9f9;
}

.audio-row {
  width: 100%;
}

.audio-icon {
  color: #409EFF;
  text-align: center;
  display: flex;
  justify-content: center;
  align-items: center;
}

.audio-description {
  text-align: center;
  font-size: 16px;
  color: #436308;
  margin-bottom: 10px;
}

.audio-player {
  width: 100%;
}

.audio-download {
  display: flex;
  text-align: center;
  /* 让按钮垂直居中 */

  justify-content: center;
  align-items: center;
}



</style>
