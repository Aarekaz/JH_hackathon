import React from "react";
import PaperUpload from "./PaperUpload";

const LandingPage: React.FC = () => {
  return (
    <div className="flex justify-center items-center h-screen ">
      <section className="flex flex-col justify-center items-center h-full w-full">
        <div className="flex flex-col justify-center items-center gap-5 max-md:flex-col">
          <div className="flex flex-col w-[74%] max-md:ml-0 max-md:w-full">
            <div className="flex z-10 flex-col self-stretch my-auto mr-0 font-light text-black max-md:mt-10 max-md:max-w-full text-center">
              <h1 className="text-5xl max-md:max-w-full max-md:text-4xl">
                <span className="font-bold text-indigo-600">AI parliament</span>{" "}
                for regulations checking of new policies
              </h1>
              <p className="self-start mt-4 ml-11 text-3xl max-md:max-w-full">
                Let the AI decide which policy is good in a{" "}
                <span className="font-bold text-indigo-600">debate</span>{" "}
                session.
              </p>
            </div>
            <PaperUpload />
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
