def predict(
        self, test_dataset: Dataset, ignore_keys: Optional[List[str]] = None, metric_key_prefix: str = "test"
    ) -> PredictionOutput:
        
        # memory metrics - must set up as early as possible
        self._memory_tracker.start()

        test_dataloader = self.get_test_dataloader(test_dataset)
        start_time = time.time()

        eval_loop = self.prediction_loop # if self.args.use_legacy_prediction_loop else self.evaluation_loop
        eval_loop(
            test_dataloader, description="Prediction", ignore_keys=ignore_keys, metric_key_prefix=metric_key_prefix
        )

def prediction_loop(
        self,
        dataloader: DataLoader,
        description: str,
        prediction_loss_only: Optional[bool] = None,
        ignore_keys: Optional[List[str]] = None,
        metric_key_prefix: str = "eval",
        output_dir: str = "/root/MLLM/LLaVA-NeXT/results",  # 새로 추가된 출력 디렉토리
    ) -> EvalLoopOutput:

        args = self.args

        if not has_length(dataloader):
            raise ValueError("dataloader must implement a working __len__")

        prediction_loss_only = prediction_loss_only if prediction_loss_only is not None else args.prediction_loss_only

        if self.is_deepspeed_enabled and self.deepspeed is None:
            _, _ = deepspeed_init(self, num_training_steps=0, inference=True)

        model = self._wrap_model(self.model, training=False, dataloader=dataloader)

        if len(self.accelerator._models) == 0 and model is self.model:
            model = (
                self.accelerator.prepare(model)
                if self.is_deepspeed_enabled
                else self.accelerator.prepare_model(model, evaluation_mode=True)
            )

            if self.is_fsdp_enabled:
                self.model = model

            if model is not self.model:
                self.model_wrapped = model

            if self.is_deepspeed_enabled:
                self.deepspeed = self.model_wrapped

        if not self.is_in_train:
            if args.fp16_full_eval:
                model = model.to(dtype=torch.float16, device=args.device)
            elif args.bf16_full_eval:
                model = model.to(dtype=torch.bfloat16, device=args.device)

        batch_size = 2 #dataloader.batch_size
        num_examples = self.num_examples(dataloader)
        logger.info(f"\n***** Running {description} *****")
        logger.info(f"  Num examples = {num_examples}")
        logger.info(f"  Batch size = {batch_size}")

        losses_host: torch.Tensor = None

        # Output file paths
        preds_file = os.path.join(output_dir, "preds.txt")
        labels_file = os.path.join(output_dir, "labels.txt")

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        model.eval()

        if args.past_index >= 0:
            self._past = None

        self.callback_handler.eval_dataloader = dataloader
        from transformers import AutoTokenizer, LlamaTokenizer
        
        model_path = "lmsys/vicuna-7b-v1.5"
        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            cache_dir=None,
            model_max_length=2048,
            padding_side="right",
            use_fast=False,
        )
        

        for step, inputs in enumerate(dataloader):
            loss, logits, labels = self.prediction_step(model, inputs, prediction_loss_only, ignore_keys=ignore_keys)
            main_input_name = getattr(self.model, "main_input_name", "input_ids")
            inputs_decode = self._prepare_input(inputs[main_input_name]) if args.include_inputs_for_metrics else None

            print("###############################")
            predicted_token_ids = torch.argmax(logits, dim=-1)
            filtered_labels0 = labels[0][labels != -100]
            filtered_labels1 = labels[1][labels != -100]
            print(len(predicted_token_ids), len(labels))
            print("aa")
            generated_text0 = tokenizer.decode(predicted_token_ids[0], skip_special_tokens=True)
            generated_text1 = tokenizer.decode(predicted_token_ids[1], skip_special_tokens=True)
            label_text0 = tokenizer.decode(filtered_labels0, skip_special_tokens=True)
            label_text1 = tokenizer.decode(filtered_labels1, skip_special_tokens=True)

            with open(preds_file, 'a') as f:
                f.write(f"{generated_text0}\n\n\n")
                f.write(f"{generated_text1}\n\n\n")
            with open(labels_file, 'a') as f:
                f.write(f"{label_text0}\n\n\n")
                f.write(f"{label_text1}\n\n\n")

            self.control = self.callback_handler.on_prediction_step(args, self.state, self.control)