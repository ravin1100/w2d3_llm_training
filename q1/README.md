# Tiny Supervised Fine-Tuning (SFT) Project

This project demonstrates a small-scale supervised fine-tuning of a language model to create a polite AI assistant.

## Project Overview

The goal of this project was to fine-tune a base language model using a small dataset of carefully crafted prompt-response pairs. The fine-tuning process aimed to:

1. Improve factual responses
2. Establish a polite tone
3. Control response length based on the context
4. Properly handle refusal cases for inappropriate requests

## Dataset

The dataset consists of 20+ prompt-response pairs covering:
- Factual Q&A examples (e.g., "Capital of France?")
- Polite-tone examples (e.g., "Please translate...")
- Short-form vs long-form answers (to demonstrate length control)
- Refusal cases (e.g., illicit request → safe denial)

Each pair is wrapped using `<|user|>` and `<|assistant|>` tokens.

## Model & Training

- **Base Model**: TinyLlama/TinyLlama-1.1B-Chat-v1.0
- **Fine-tuning Method**: LoRA (Low-Rank Adaptation) with PEFT
- **Training Parameters**:
  - Epochs: 3
  - Learning Rate: 5e-5
  - LoRA Rank: 8
  - LoRA Alpha: 16

## Results

The fine-tuned model shows significant improvements over the base model in several areas:

1. **Factual Accuracy**: Provides correct answers to factual questions
2. **Response Format**: Maintains proper structure with appropriate tokens
3. **Length Control**: Adjusts response length based on the query type
4. **Refusal Handling**: Shows improvement in handling inappropriate requests
5. **Overall Quality**: Delivers more coherent and appropriately formatted responses

For detailed comparisons, see [before_after.md](before_after.md).

### Evaluation Screenshot

Below is a screenshot of the evaluation results comparing the base model and fine-tuned model:

![Evaluation Results](evaluation_screenshot.png)

## Project Structure

- `dataset.json`: Contains the prompt-response pairs for training
- `train.py`: Script for fine-tuning the model using PEFT/LoRA
- `evaluate.py`: Script for evaluating model responses
- `before_after.md`: Comparison of responses before and after fine-tuning
- `base_responses.txt`: Raw responses from the base model
- `finetuned_responses.txt`: Raw responses from the fine-tuned model
- `evaluation_screenshot.png`: Visual comparison of model responses
- `README.md`: This file

## Setup & Usage

### Requirements

```
pip install -r requirements.txt
```

### Evaluating the Base Model

```
python evaluate.py
```

### Training the Model

```
python train.py
```

### Evaluating the Fine-tuned Model

```
python evaluate.py --model_path ./finetuned_model
```

## Using Google Colab

This project is well-suited for running on Google Colab, which provides free GPU resources for training. To use Colab:

1. **Upload Project Files**: Upload all project files to a Colab notebook session or connect to your Google Drive
   
2. **Install Dependencies**:
   ```python
   !pip install transformers datasets torch peft accelerate bitsandbytes
   ```

3. **GPU Configuration**: Ensure you've enabled GPU runtime by going to:
   `Runtime > Change runtime type > Hardware accelerator > GPU`

4. **Training Process**:
   ```python
   !python train.py
   ```

5. **Evaluation**:
   ```python
   # Evaluate base model
   !python evaluate.py
   
   # Evaluate fine-tuned model
   !python evaluate.py --model_path ./finetuned_model
   ```

6. **Saving Results**: Download the fine-tuned model and evaluation results to your local machine:
   ```python
   from google.colab import files
   !zip -r finetuned_model.zip finetuned_model/
   !zip -r evaluation_results.zip base_responses.txt finetuned_responses.txt before_after.md
   files.download('finetuned_model.zip')
   files.download('evaluation_results.zip')
   ```

Using Colab is recommended for this project as fine-tuning language models requires significant computational resources that might not be available on a typical personal computer.

## Future Improvements

- Expand the dataset with more diverse examples
- Improve refusal handling for harmful requests
- Experiment with different LoRA configurations
- Implement more rigorous evaluation metrics 