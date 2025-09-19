const express = require('express');
const cors = require('cors');
const fs = require('fs').promises;
const path = require('path');

const app = express();
const PORT = 3000;
const DATA_FILE = path.join(__dirname, 'data.json');

app.use(cors());
app.use(express.json());

const loadData = async () => {
  try {
    const data = await fs.readFile(DATA_FILE, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    return [];
  }
};

const saveData = async (data) => {
  await fs.writeFile(DATA_FILE, JSON.stringify(data, null, 2));
};

app.get('/files', async (req, res) => {
  try {
    const files = await loadData();
    res.json(files);
  } catch (error) {
    res.status(500).json({ error: 'Failed to load files' });
  }
});

app.get('/files/:id', async (req, res) => {
  try {
    const files = await loadData();
    const file = files.find(f => f.id === req.params.id);
    if (!file) {
      return res.status(404).json({ error: 'File not found' });
    }
    res.json(file);
  } catch (error) {
    res.status(500).json({ error: 'Failed to load file' });
  }
});

app.post('/files', async (req, res) => {
  try {
    const { name, content } = req.body;
    if (!name || !content) {
      return res.status(400).json({ error: 'Name and content are required' });
    }
    
    const files = await loadData();
    const newFile = {
      id: Date.now().toString(),
      name,
      content,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    
    files.push(newFile);
    await saveData(files);
    res.status(201).json(newFile);
  } catch (error) {
    res.status(500).json({ error: 'Failed to create file' });
  }
});

app.put('/files/:id', async (req, res) => {
  try {
    const { name, content } = req.body;
    const files = await loadData();
    const fileIndex = files.findIndex(f => f.id === req.params.id);
    
    if (fileIndex === -1) {
      return res.status(404).json({ error: 'File not found' });
    }
    
    files[fileIndex] = {
      ...files[fileIndex],
      name: name || files[fileIndex].name,
      content: content || files[fileIndex].content,
      updatedAt: new Date().toISOString()
    };
    
    await saveData(files);
    res.json(files[fileIndex]);
  } catch (error) {
    res.status(500).json({ error: 'Failed to update file' });
  }
});

app.delete('/files/:id', async (req, res) => {
  try {
    const files = await loadData();
    const fileIndex = files.findIndex(f => f.id === req.params.id);
    
    if (fileIndex === -1) {
      return res.status(404).json({ error: 'File not found' });
    }
    
    files.splice(fileIndex, 1);
    await saveData(files);
    res.status(204).send();
  } catch (error) {
    res.status(500).json({ error: 'Failed to delete file' });
  }
});

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
  console.log('Available endpoints:');
  console.log('GET    /files      - Get all files');
  console.log('GET    /files/:id  - Get file by ID');
  console.log('POST   /files      - Create new file');
  console.log('PUT    /files/:id  - Update file');
  console.log('DELETE /files/:id  - Delete file');
});