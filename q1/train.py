import json
import os
os.environ["WANDB_DISABLED"] = "true"  # Disable wandb before it's initialized
os.environ["WANDB_MODE"] = "offline"  # Force offline mode as a backup
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer, DataCollatorForLanguageModeling
from datasets import Dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
import torch.distributed as dist

def process_example(example):
    """Process a single example from the dataset."""
    messages = example["messages"]
    # Process the prompt-response pair
    prompt = next(msg["content"] for msg in messages if msg["role"] == "user")
    response = next(msg["content"] for msg in messages if msg["role"] == "assistant")
    return {"prompt": prompt, "response": response}

def main():
    # Load dataset
    with open("dataset.json", "r") as f:
        data = json.load(f)
    
    processed_data = [process_example(example) for example in data]
    dataset = Dataset.from_list(processed_data)
    
    # Split dataset into train and validation
    dataset = dataset.train_test_split(test_size=0.1)
    
    # Load tokenizer and model - using a smaller model
    model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # Smaller model with 1.1B parameters
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token
    
    # Load model in 8-bit to reduce memory usage
    model = AutoModelForCausalLM.from_pretrained(
        model_name, 
        load_in_8bit=True,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    # Prepare model for k-bit training
    model = prepare_model_for_kbit_training(model)
    
    # Configure LoRA
    lora_config = LoraConfig(
        r=8,  # Reduced rank for smaller model
        lora_alpha=16,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],  # Adjusted for TinyLlama architecture
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    
    # Apply LoRA to model
    model = get_peft_model(model, lora_config)
    
    # Print trainable parameters
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    all_params = sum(p.numel() for p in model.parameters())
    print(f"Trainable parameters: {trainable_params} ({100 * trainable_params / all_params:.2f}% of all parameters)")
    
    # Define tokenization function for causal language modeling
    def tokenize_function(examples):
        # Combine prompt and response for training
        texts = [p + r for p, r in zip(examples["prompt"], examples["response"])]
        
        # Tokenize with padding and truncation
        tokenized = tokenizer(
            texts,
            padding="max_length",
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )
        
        # Set up labels for causal language modeling (same as input_ids)
        tokenized["labels"] = tokenized["input_ids"].clone()
        
        return tokenized
    
    # Tokenize datasets
    tokenized_datasets = dataset.map(tokenize_function, batched=True, remove_columns=dataset["train"].column_names)
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False  # Not using masked language modeling
    )
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir="./results",
        num_train_epochs=3,
        per_device_train_batch_size=8,  # Increased batch size for smaller model
        per_device_eval_batch_size=8,
        gradient_accumulation_steps=4,  # Reduced for smaller model
        learning_rate=5e-5,
        fp16=True,
        logging_steps=10,
        eval_strategy="epoch",  # Changed from evaluation_strategy to eval_strategy
        save_strategy="epoch",
        load_best_model_at_end=True,
        push_to_hub=False,
        report_to="none",  # Explicitly disable all reporting
    )
    
    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["test"],
        data_collator=data_collator,
    )
    
    # Train model
    trainer.train()
    
    # Save model
    model.save_pretrained("./finetuned_model")
    tokenizer.save_pretrained("./finetuned_model")
    
    print("Training complete. Model saved to ./finetuned_model")

if __name__ == "__main__":
    main() 