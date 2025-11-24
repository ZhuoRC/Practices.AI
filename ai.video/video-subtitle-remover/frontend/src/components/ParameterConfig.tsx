import React from 'react';
import { Settings, Info, Cpu, Zap, Palette } from 'lucide-react';
import { ProcessConfig } from '../types';

interface ParameterConfigProps {
  config: ProcessConfig;
  onChange: (config: ProcessConfig) => void;
}

export const ParameterConfig: React.FC<ParameterConfigProps> = ({
  config,
  onChange,
}) => {
  const updateConfig = (updates: Partial<ProcessConfig>) => {
    onChange({
      ...config,
      ...updates,
    });
  };

  const updateSttnParams = (updates: Partial<NonNullable<typeof config.sttnParams>>) => {
    onChange({
      ...config,
      sttnParams: {
        ...config.sttnParams,
        ...updates,
      },
    });
  };

  const updatePropainterParams = (updates: Partial<NonNullable<typeof config.propainterParams>>) => {
    onChange({
      ...config,
      propainterParams: {
        ...config.propainterParams,
        ...updates,
      },
    });
  };

  const updateLamaParams = (updates: Partial<NonNullable<typeof config.lamaParams>>) => {
    onChange({
      ...config,
      lamaParams: {
        ...config.lamaParams,
        ...updates,
      },
    });
  };

  const updateCommonParams = (updates: Partial<NonNullable<typeof config.commonParams>>) => {
    onChange({
      ...config,
      commonParams: {
        ...config.commonParams,
        ...updates,
      },
    });
  };

  return (
    <div className="space-y-6">
      {/* 修复算法选择 */}
      <div className="card">
        <div className="card-header">
          <div className="flex items-center space-x-2">
            <Cpu className="w-5 h-5 text-primary-600" />
            <h3 className="font-semibold text-gray-900 dark:text-dark-text">
              修复算法
            </h3>
          </div>
        </div>
        <div className="card-body space-y-4">
          <div className="grid grid-cols-1 gap-3">
            {[
              {
                value: 'sttn',
                label: 'STTN',
                description: '真人视频效果好，速度快，可跳过字幕检测',
                icon: <Zap className="w-4 h-4" />,
                recommended: true,
              },
              {
                value: 'lama',
                label: 'LAMA',
                description: '图片效果最好，动画类视频效果好',
                icon: <Palette className="w-4 h-4" />,
                recommended: false,
              },
              {
                value: 'propainter',
                label: 'ProPainter',
                description: '运动剧烈视频效果好，需要大量显存',
                icon: <Cpu className="w-4 h-4" />,
                recommended: false,
              },
            ].map((option) => (
              <label
                key={option.value}
                className={`
                  relative p-4 border rounded-lg cursor-pointer transition-all
                  ${config.algorithm === option.value
                    ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                    : 'border-gray-300 dark:border-gray-600 hover:border-gray-400'
                  }
                `}
              >
                <div className="flex items-start space-x-3">
                  <input
                    type="radio"
                    name="algorithm"
                    value={option.value}
                    checked={config.algorithm === option.value}
                    onChange={(e) => updateConfig({ algorithm: e.target.value as any })}
                    className="mt-1"
                  />
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      {option.icon}
                      <span className="font-medium text-gray-900 dark:text-dark-text">
                        {option.label}
                      </span>
                      {option.recommended && (
                        <span className="badge badge-primary text-xs">推荐</span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      {option.description}
                    </p>
                  </div>
                </div>
              </label>
            ))}
          </div>
        </div>
      </div>

      {/* 算法特定参数 */}
      {config.algorithm === 'sttn' && (
        <div className="card">
          <div className="card-header">
            <h3 className="font-semibold text-gray-900 dark:text-dark-text flex items-center space-x-2">
              <Info className="w-4 h-4" />
              <span>STTN 算法参数</span>
            </h3>
          </div>
          <div className="card-body space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                跳过字幕检测
              </label>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={config.sttnParams?.skipDetection || false}
                  onChange={(e) => updateSttnParams({ skipDetection: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                相邻帧步长: {config.sttnParams?.neighborStride || 5}
              </label>
              <input
                type="range"
                min="1"
                max="20"
                value={config.sttnParams?.neighborStride || 5}
                onChange={(e) => updateSttnParams({ neighborStride: parseInt(e.target.value) })}
                className="slider w-full mt-1"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>1</span>
                <span>20</span>
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                参考帧长度: {config.sttnParams?.referenceLength || 10}
              </label>
              <input
                type="range"
                min="5"
                max="30"
                value={config.sttnParams?.referenceLength || 10}
                onChange={(e) => updateSttnParams({ referenceLength: parseInt(e.target.value) })}
                className="slider w-full mt-1"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>5</span>
                <span>30</span>
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                最大加载数量: {config.sttnParams?.maxLoadNum || 50}
              </label>
              <input
                type="range"
                min="10"
                max="100"
                value={config.sttnParams?.maxLoadNum || 50}
                onChange={(e) => updateSttnParams({ maxLoadNum: parseInt(e.target.value) })}
                className="slider w-full mt-1"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>10</span>
                <span>100</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {config.algorithm === 'propainter' && (
        <div className="card">
          <div className="card-header">
            <h3 className="font-semibold text-gray-900 dark:text-dark-text flex items-center space-x-2">
              <Info className="w-4 h-4" />
              <span>ProPainter 算法参数</span>
            </h3>
          </div>
          <div className="card-body space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                最大加载数量: {config.propainterParams?.maxLoadNum || 70}
              </label>
              <input
                type="range"
                min="10"
                max="100"
                value={config.propainterParams?.maxLoadNum || 70}
                onChange={(e) => updatePropainterParams({ maxLoadNum: parseInt(e.target.value) })}
                className="slider w-full mt-1"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>10</span>
                <span>100</span>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                根据GPU显存调整，70需要约8G显存
              </p>
            </div>
          </div>
        </div>
      )}

      {config.algorithm === 'lama' && (
        <div className="card">
          <div className="card-header">
            <h3 className="font-semibold text-gray-900 dark:text-dark-text flex items-center space-x-2">
              <Info className="w-4 h-4" />
              <span>LAMA 算法参数</span>
            </h3>
          </div>
          <div className="card-body space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                极速模式
              </label>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={config.lamaParams?.superFast || false}
                  onChange={(e) => updateLamaParams({ superFast: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              极速模式不保证修复效果，仅对文本区域进行简单去除
            </p>
          </div>
        </div>
      )}

      {/* 通用参数 */}
      <div className="card">
        <div className="card-header">
          <h3 className="font-semibold text-gray-900 dark:text-dark-text flex items-center space-x-2">
            <Settings className="w-4 h-4" />
            <span>通用参数</span>
          </h3>
        </div>
        <div className="card-body space-y-4">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              使用 H264 编码
            </label>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={config.commonParams?.useH264 ?? true}
                onChange={(e) => updateCommonParams({ useH264: e.target.checked })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            启用后生成的视频在安卓手机上兼容性更好
          </p>

          <div>
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              高度宽度差异阈值: {config.commonParams?.thresholdHeightWidthDifference || 10}px
            </label>
            <input
              type="range"
              min="1"
              max="50"
              value={config.commonParams?.thresholdHeightWidthDifference || 10}
              onChange={(e) => updateCommonParams({ thresholdHeightWidthDifference: parseInt(e.target.value) })}
              className="slider w-full mt-1"
            />
          </div>

          <div>
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              字幕区域偏差像素: {config.commonParams?.subtitleAreaDeviationPixel || 20}px
            </label>
            <input
              type="range"
              min="1"
              max="50"
              value={config.commonParams?.subtitleAreaDeviationPixel || 20}
              onChange={(e) => updateCommonParams({ subtitleAreaDeviationPixel: parseInt(e.target.value) })}
              className="slider w-full mt-1"
            />
          </div>

          <div>
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              高度差异阈值: {config.commonParams?.thresholdHeightDifference || 20}px
            </label>
            <input
              type="range"
              min="1"
              max="50"
              value={config.commonParams?.thresholdHeightDifference || 20}
              onChange={(e) => updateCommonParams({ thresholdHeightDifference: parseInt(e.target.value) })}
              className="slider w-full mt-1"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Y轴像素容差: {config.commonParams?.pixelToleranceY || 20}px
              </label>
              <input
                type="range"
                min="1"
                max="50"
                value={config.commonParams?.pixelToleranceY || 20}
                onChange={(e) => updateCommonParams({ pixelToleranceY: parseInt(e.target.value) })}
                className="slider w-full mt-1"
              />
            </div>

            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                X轴像素容差: {config.commonParams?.pixelToleranceX || 20}px
              </label>
              <input
                type="range"
                min="1"
                max="50"
                value={config.commonParams?.pixelToleranceX || 20}
                onChange={(e) => updateCommonParams({ pixelToleranceX: parseInt(e.target.value) })}
                className="slider w-full mt-1"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
