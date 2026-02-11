function drawConstellation(iqData) {
    const canvas = document.getElementById('iq-canvas');
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Draw background
    ctx.fillStyle = '#f8f9fa';
    ctx.fillRect(0, 0, width, height);

    // Draw grid
    ctx.strokeStyle = '#ccc';
    ctx.lineWidth = 1;

    // Horizontal
    ctx.beginPath();
    ctx.moveTo(0, height/2);
    ctx.lineTo(width, height/2);
    ctx.stroke();

    // Vertical
    ctx.beginPath();
    ctx.moveTo(width/2, 0);
    ctx.lineTo(width/2, height);
    ctx.stroke();

    // Scale points to fit canvas
    // Assume points are within [-2, 2] roughly for BPSK/QPSK with noise, maybe more for QAM
    // Let's find max value to scale
    let maxVal = 0;
    for(let i=0; i<iqData.length; i++) {
        maxVal = Math.max(maxVal, Math.abs(iqData[i][0]), Math.abs(iqData[i][1]));
    }

    // Add some padding, ensure minimum scale for BPSK/QPSK
    const scaleMax = Math.max(2.0, maxVal * 1.2);

    const scale = (width / 2) / scaleMax;

    ctx.fillStyle = 'rgba(0, 0, 255, 0.5)';

    iqData.forEach(pt => {
        const i = pt[0];
        const q = pt[1];

        // Transform to canvas coords
        // Center is (width/2, height/2)
        // x = center + i * scale
        // y = center - q * scale (y grows downwards)

        const x = width/2 + i * scale;
        const y = height/2 - q * scale;

        ctx.beginPath();
        ctx.arc(x, y, 2, 0, 2 * Math.PI);
        ctx.fill();
    });
}
