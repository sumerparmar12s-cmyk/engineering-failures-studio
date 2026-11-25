"""Generate AI clips/stills from ai/prompts.json (skips existing). usage: gen.py video|still"""
import sys, os, json, time, torch
torch.set_num_threads(4)
P = os.path.dirname(os.path.abspath(__file__)); J = json.load(open(f'{P}/prompts.json')); kind = sys.argv[1]
NEG = 'cartoon, anime, illustration, text, letters, logo, watermark, blurry, deformed, low quality, painting'
if kind == 'video':
    from diffusers import AnimateDiffPipeline, MotionAdapter, EulerDiscreteScheduler
    from huggingface_hub import hf_hub_download
    from safetensors.torch import load_file
    ad = MotionAdapter().to('cpu', torch.float32)
    ad.load_state_dict(load_file(hf_hub_download('ByteDance/AnimateDiff-Lightning', 'animatediff_lightning_4step_diffusers.safetensors')))
    p = AnimateDiffPipeline.from_pretrained('emilianJR/epiCRealism', motion_adapter=ad, torch_dtype=torch.float32)
    p.scheduler = EulerDiscreteScheduler.from_config(p.scheduler.config, timestep_spacing='trailing', beta_schedule='linear')
    p.vae.enable_slicing()
    for name, pr in J['video'].items():
        d = f'{P}/video/{name}'
        if os.path.exists(f'{d}/015.png'): continue
        os.makedirs(d, exist_ok=True); t = time.time()
        g = torch.Generator().manual_seed(abs(hash(name)) % 10000)
        out = p(prompt=pr, negative_prompt=NEG, guidance_scale=1.0, num_inference_steps=4, num_frames=16, width=576, height=320, generator=g, decode_chunk_size=2)
        for i, f in enumerate(out.frames[0]): f.save(f'{d}/{i:03d}.png')
        print(name, round(time.time() - t), 's', flush=True)
else:
    from diffusers import AutoPipelineForText2Image
    p = AutoPipelineForText2Image.from_pretrained('stabilityai/sdxl-turbo', torch_dtype=torch.float32)
    os.makedirs(f'{P}/still', exist_ok=True)
    for name, pr in J['still'].items():
        f = f'{P}/still/{name}.png'
        if os.path.exists(f): continue
        t = time.time()
        for k in range(2):   # two variants, pick later
            im = p(prompt=pr + ', 35mm film, natural light', negative_prompt=NEG, num_inference_steps=3, guidance_scale=0.0, width=1024, height=576, generator=torch.Generator().manual_seed(k * 77 + 5)).images[0]
            im.save(f'{P}/still/{name}_{k}.png')
        os.replace(f'{P}/still/{name}_0.png', f)
        print(name, round(time.time() - t), 's', flush=True)
print('GEN DONE', kind, flush=True)
