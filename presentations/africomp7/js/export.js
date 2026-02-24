document.addEventListener('DOMContentLoaded', () => {
    const downloadPdfBtn = document.getElementById('downloadPdfBtn');
    if (!downloadPdfBtn) return;

    downloadPdfBtn.addEventListener('click', async function(e) {
        e.preventDefault();
        
        if (typeof html2canvas === 'undefined' || typeof jspdf === 'undefined') {
            alert("PDF libraries are still loading. Please try again in a moment or refresh the page.");
            return;
        }

        const { jsPDF } = window.jspdf;

        // Custom button loading state
        const originalText = this.innerHTML;
        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating PDF...';
        this.style.pointerEvents = 'none';

        // Prepare body for export
        document.documentElement.classList.add('pdf-export-mode');
        document.body.classList.add('pdf-export-mode');
        
        // Get all slides
        const slides = document.querySelectorAll('.slide');
        
        // Create PDF instance - landscape, 1920x1080 resolution
        const pdf = new jsPDF({
            orientation: 'landscape',
            unit: 'px',
            format: [1920, 1080]
        });

        // Keep track of the original scroll position
        const originalScrollY = window.scrollY;

        try {
            for (let i = 0; i < slides.length; i++) {
                const slide = slides[i];
                
                // Scroll slide into view so html2canvas sees it perfectly on-screen
                slide.scrollIntoView({ behavior: 'instant', block: 'start' });
                
                // Yield to browser rendering pipeline before capturing
                await new Promise(resolve => setTimeout(resolve, 80));

                const canvas = await html2canvas(slide, {
                    scale: 2,           // High DPI capture
                    width: 1920,        // Force dimensions
                    height: 1080,
                    windowWidth: 1920,
                    useCORS: true,      // Allow images to load
                    logging: false,     // Keep console clean
                    // We let it calculate X and Y naturally since we scrolled to it.
                });

                const imgData = canvas.toDataURL('image/jpeg', 0.98);

                // Add a new page for all slides after the first
                if (i > 0) {
                    pdf.addPage([1920, 1080], 'landscape');
                }

                pdf.addImage(imgData, 'JPEG', 0, 0, 1920, 1080);
            }

            // Trigger the download of the completed PDF
            pdf.save('AfriComp7_Paul_Namalomba_Presentation.pdf');
        } catch (err) {
            console.error("PDF generation error: ", err);
            alert("An error occurred during PDF generation. Check console for details.");
        } finally {
            // Restore state
            document.documentElement.classList.remove('pdf-export-mode');
            document.body.classList.remove('pdf-export-mode');
            this.innerHTML = originalText;
            this.style.pointerEvents = 'auto';
            
            // Scroll back to where the user was
            window.scrollTo({top: originalScrollY, left: 0, behavior: 'instant'});
        }
    });
});
