import React from 'react';
import ReactDOM from 'react-dom/client';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConfigProvider
      locale={zhCN}
      theme={{
        token: {
          colorText: '#1a1a1a',
          colorTextSecondary: '#4a4a4a',
          colorTextTertiary: '#6a6a6a',
          colorTextDescription: '#4a4a4a',
        },
      }}
    >
      <App />
    </ConfigProvider>
  </React.StrictMode>,
);
